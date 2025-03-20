from typing import Sequence

from django.contrib.postgres.expressions import ArraySubquery
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    Func,
    F,
    Q,
    DateTimeField,
    When,
    Case,
    Value,
    OuterRef,
)
from django.db.models.functions import Cast
from django_cte import With, CTEManager

from django_pg_rrule.fields import RruleField
from datetime import datetime


class AtTimeZone(Func):
    """Cast value to timestamp with a certain time zone."""

    template = "(%(expressions)s) AT TIME ZONE %(time_zone)s"

    def __init__(self, expression, time_zone):
        self.time_zone = time_zone
        super().__init__(expression)

    def as_sql(self, compiler, connection, **extra_context):
        extra_context["time_zone"] = self.time_zone
        return super().as_sql(compiler, connection, **extra_context)


class CastTimestamp(Cast):
    """Cast value to timestamp without time zone."""

    def as_sql(self, compiler, connection, **extra_context):
        extra_context["db_type"] = "timestamp"
        return Func.as_sql(self, compiler, connection, **extra_context)


class RecurrenceManager(CTEManager):
    date_start_field = "date_start"
    date_end_field = "date_end"
    datetime_start_field = "datetime_start"
    datetime_end_field = "datetime_end"
    until_field = "rrule_until"
    amends_field = "amends"
    amended_by_field = "amended_by"

    def _get_odatetime(
        self,
        start: datetime,
        end: datetime,
        expand_start: datetime | None = None,
        expand_end: datetime | None = None,
    ):
        """Get subquery part for evaluated datetime."""
        min_end = min(expand_end, end) if expand_end else end
        return Func(
            Case(
                When(
                    condition=Q(rrule__isnull=False),
                    then=Func(
                        # get_occurrences
                        Func(
                            # rrule
                            Cast("rrule", output_field=RruleField()),
                            # datetime start
                            AtTimeZone(
                                Case(
                                    When(
                                        **{
                                            f"{self.datetime_start_field}__lt": expand_start
                                        },
                                        then=expand_start,
                                    ),
                                    default=F(self.datetime_start_field),
                                )
                                if expand_start
                                else F(self.datetime_start_field),
                                time_zone="core_calendarevent.timezone",
                            ),
                            # until
                            AtTimeZone(
                                Case(
                                    When(
                                        **{f"{self.until_field}__gt": min_end},
                                        then=min_end,
                                    ),
                                    default=F(self.until_field),
                                ),
                                time_zone="core_calendarevent.timezone",
                            ),
                            function="get_occurrences",
                            output_field=DateTimeField(),
                        ),
                        F("rdatetimes"),
                        function="ARRAY_CAT",
                        output_field=ArrayField(DateTimeField()),
                    ),
                ),
                default=Func(
                    Value("{}", output_field=ArrayField(DateTimeField())),
                    F(self.datetime_start_field),
                    function="ARRAY_APPEND",
                    output_field=ArrayField(DateTimeField()),
                ),
            ),
            function="UNNEST",
            output_field=DateTimeField(),
        )

    def _get_odate(
        self,
        start: datetime,
        end: datetime,
        expand_start: datetime | None = None,
        expand_end: datetime | None = None,
    ):
        """Get subquery part for evaluated date."""
        return Func(
            Case(
                When(
                    condition=Q(rrule__isnull=False),
                    then=Func(
                        Func(
                            Cast("rrule", output_field=RruleField()),
                            Case(
                                When(
                                    **{f"{self.date_start_field}__lt": expand_start},
                                    then=expand_start,
                                ),
                                default=F(self.date_start_field),
                            )
                            if expand_start
                            else F(self.date_start_field),
                            min(expand_end, end) if expand_end else end,
                            function="get_occurrences",
                            output_field=DateTimeField(),
                        ),
                        Cast("rdates", output_field=ArrayField(DateTimeField())),
                        function="ARRAY_CAT",
                        output_field=ArrayField(DateTimeField()),
                    ),
                ),
                default=Func(
                    Value("{}", output_field=ArrayField(DateTimeField())),
                    Cast(self.date_start_field, output_field=DateTimeField()),
                    function="ARRAY_APPEND",
                    output_field=ArrayField(DateTimeField()),
                ),
            ),
            function="UNNEST",
        )

    def with_occurrences(
        self,
        start: datetime,
        end: datetime,
        expand_start: datetime | None = None,
        expand_end: datetime | None = None,
        start_qs: Q | None = None,
        additional_filter: Q | None = None,
        select_related: Sequence | None = None,
        prefetch_related: Sequence | None = None,
        order_by: Sequence | None = None,
        expand: bool | None = False,
    ):
        """Evaluate rrules and annotate all occurrences."""

        start_qs = self if start_qs is None else start_qs

        with_qs = start_qs.filter(
            (
                Q(**{f"{self.datetime_start_field}__lte": end})
                | Q(**{f"{self.date_start_field}__lte": end.date()})
            )
            & (
                Q(**{f"{self.until_field}__isnull": True})
                | Q(
                    **{
                        f"{self.until_field}__gte": expand_start
                        if expand_start
                        else start
                    }
                )
            )
        )
        if additional_filter:
            with_qs = with_qs.filter(additional_filter)

        annotated_with_qs = with_qs.annotate(
            odatetime=self._get_odatetime(start, end, expand_start, expand_end),
            odate=self._get_odate(start, end, expand_start, expand_end),
        )

        cte = With(
            annotated_with_qs.only("id"),
            name="qodatetimes",
        )
        qs = (  # Join WITH clause with actual data
            cte.join(self.model, id=cte.col.id)
            .with_cte(cte)
            # Annotate WITH clause
            .annotate(odatetime_t=cte.col.odatetime, odate=cte.col.odate)
            .annotate(
                odatetime=Case(
                    When(
                        condition=Q(rrule__isnull=False),
                        then=AtTimeZone(
                            CastTimestamp("odatetime_t", output_field=DateTimeField()),
                            time_zone="core_calendarevent.timezone",
                        ),
                    ),
                    default=F("odatetime_t"),
                )
            )
        )

        expanded_qs_in_range = (
            qs.exclude(
                # Exclude exdatetimes and exdates
                (Q(odatetime__isnull=False) & Q(exdatetimes__contains=[F("odatetime")]))
                | (Q(odate__isnull=False) & Q(exdates__contains=[F("odate")]))
            )
            .annotate(test1=start - (F("datetime_end") - F("datetime_start")))
            .filter(
                # With rrule, filter recurrences
                Q(
                    odatetime__lt=end,
                    odatetime__gt=start - (F("datetime_end") - F("datetime_start")),
                )
                | Q(
                    odate__lte=end.date(),
                    odate__gte=start.date() - (F("date_end") - F("date_start")),
                )
            )
        )

        if expand:
            qs = expanded_qs_in_range
            amending_events = qs.filter(**{self.amends_field: OuterRef("pk")})

            qs = qs.annotate(
                amended_by_odatetimes=Case(
                    When(
                        Q(
                            **{
                                f"{self.amended_by_field}__isnull": False,
                                "odatetime__isnull": False,
                            }
                        ),
                        then=ArraySubquery(
                            amending_events.values("odatetime"),
                        ),
                    ),
                    default=Value([], output_field=ArrayField(DateTimeField())),
                ),
                amended_by_odates=Case(
                    When(
                        Q(
                            **{
                                f"{self.amended_by_field}__isnull": False,
                                "odate__isnull": False,
                            }
                        ),
                        then=ArraySubquery(
                            amending_events.values("odate"),
                        ),
                    ),
                    default=Value([], output_field=ArrayField(DateTimeField())),
                ),
            )

            qs = qs.exclude(
                (
                    Q(odatetime__isnull=False)
                    & Q(amended_by_odatetimes__len__gt=0)
                    & Q(amended_by_odatetimes__contains=[F("odatetime")])
                )
                | (
                    Q(odate__isnull=False)
                    & Q(amended_by_odates__len__gt=0)
                    & Q(amended_by_odates__contains=[F("odate")])
                )
            )
        else:
            qs = with_qs.filter(
                Q(id__in=expanded_qs_in_range.values_list("id", flat=True))
            )

        if select_related:
            qs = qs.select_related(*select_related)

        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)

        if order_by:
            qs = qs.order_by(*order_by)

        if expand:
            # Hacky way to enforce RIGHT OUTER JOIN
            # Otherwise, Django always will rewrite the join_type to LEFT OUTER JOIN/INNER JOIN
            qs.query.alias_map["qodatetimes"].join_type = "RIGHT OUTER JOIN"

        return qs
