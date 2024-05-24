from datetime import timedelta

from django.db import models
from django.db.models import Avg, Count, F, Max, Min, OuterRef, Subquery, Sum, Value
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import DateTimeField
from django.db.models.functions import (
    Concat,
    ExtractHour,
    ExtractMinute,
    Round,
    TruncDay,
    TruncHour,
)


class CumulativeMeasurementsQuerySet(models.QuerySet):
    """
    This class defines custom Queryset to aggregate data from CumulativeMeasurements.

    The collection_date field is adjusted by subtracting 15 minutes to reflect the previous hour.
    This adjustment is necessary because the data is collected every 15 minutes, and the data
    is stored from 00:00 to 23:45. For hourly aggregation, adjusted to 23:45, reflecting the previous
    hour from 00:00 to 23:59.
    """

    def aggregate_hourly(self, agg_type, fields):
        adjusted_hour = ExpressionWrapper(
            F("collection_date") - timedelta(minutes=15),
            output_field=DateTimeField(),
        )

        annotations = {}
        for field in fields:
            agg_func = self._get_aggregate_function(agg_type, field)
            annotations[field] = agg_func

        return (
            self.annotate(date=TruncHour(adjusted_hour))  #
            .values("date")
            .annotate(**annotations, hour=ExtractHour("date"))
            .order_by("date")
        )

    def aggregate_daily(self, agg_type, fields):
        adjusted_date = ExpressionWrapper(
            F("collection_date") - timedelta(minutes=15),
            output_field=DateTimeField(),
        )

        annotations = {}
        for field in fields:
            agg_func = self._get_aggregate_function(agg_type, field)
            annotations[field] = agg_func

        return (
            self.annotate(daily=TruncDay(adjusted_date))  #
            .values("daily")
            .annotate(**annotations)
            .order_by("daily")
        )

    # Django USE_TZ = True => Filter by UTC hour (UTC-3)
    def aggregate_peak_hours(self, fields):
        data_agg_hourly = self.aggregate_hourly("sum", fields)
        peak_hours_data = data_agg_hourly.filter(
            hour__gte=21,  # 18:00 - 20:59 (UTC-3)
            hour__lte=23,
        )
        for item in peak_hours_data:
            item.pop("hour")

        return peak_hours_data

    # Django USE_TZ = True => Filter by UTC hour (UTC-3)
    def aggregate_off_peak_hours(self, fields):
        data_agg_hourly = self.aggregate_hourly("sum", fields)
        peak_off_hours_data = data_agg_hourly.exclude(
            hour__gte=21,  # 18:00 - 20:59 (UTC-3)
            hour__lt=23,
        )
        for item in peak_off_hours_data:
            item.pop("hour")

        return peak_off_hours_data

    def quarter_hourly_avg(self, fields):
        annotations = {field: Round(Avg(field), 2) for field in fields}

        return (
            self.annotate(
                hour=ExtractHour("collection_date"),
                minute=ExtractMinute("collection_date"),
                time=Concat("hour", Value(":"), "minute", output_field=models.TimeField()),
            )
            .values("time")
            .annotate(**annotations)
            .order_by("time")
        )

    def _get_aggregate_function(self, agg_type, field):
        aggregate_function = {
            "avg": Round(Avg(field), 2),
            "sum": Round(Sum(field), 2),
            "min": Round(Min(field), 2),
            "max": Round(Max(field), 2),
            "count": Count(field),
        }

        try:
            return aggregate_function[agg_type]
        except KeyError:
            raise ValueError(f"Invalid aggregation type: {agg_type}")


class CumulativeMeasurementsManager(models.Manager):
    def get_queryset(self):
        return CumulativeMeasurementsQuerySet(self.model, using=self._db)

    def aggregate_hourly(self, agg_type, agg_field):
        return self.get_queryset().hourly(agg_type, agg_field)

    def aggregate_daily(self, agg_type, agg_field):
        return self.get_queryset().daily(agg_type, agg_field)

    def aggregate_peak_hours(self, agg_field):
        return self.get_queryset().peak_hours(agg_field)

    def aggregate_off_peak_hours(self, agg_field):
        return self.get_queryset().off_peak_hours(agg_field)

    def quarter_hourly_avg(self, agg_field):
        return self.get_queryset().quarter_hourly_avg(agg_field)
