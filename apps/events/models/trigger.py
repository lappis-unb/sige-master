import logging
from datetime import timedelta

from django.db import models
from django.db.models import Avg, Max, Min
from django.utils import timezone
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.events.models import EventType
from apps.measurements.models import CumulativeMeasurement
from apps.utils.helpers import get_dynamic_fields

logger = logging.getLogger("apps")


class Trigger(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class CompareOperator(models.TextChoices):
    GT = "gt", _("> (Greater Than)")
    GTE = "gte", _(">= (Greater Than or Equal)")
    LT = "lt", _("< (Less Than)")
    LTE = "lte", _("<= (Less Than or Equal)")
    EXACT = "exact", _("== (Equal)")
    NE = "ne", _("!= (Not Equal)")


class InstantMeasurementTrigger(Trigger):
    operator = models.CharField(max_length=5, choices=CompareOperator.choices)
    active_threshold = models.FloatField(blank=True, null=True)
    deactivate_threshold = models.FloatField(blank=True, null=True)
    field_name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        choices=lazy(get_dynamic_fields, list)("measurements", "InstantMeasurement"),
    )

    class Meta:
        verbose_name = _("Instant Measurement Trigger")
        verbose_name_plural = _("Instant Measurement Triggers")

    def __str__(self):
        return f"{self.name}"


class DynamicMetric(models.TextChoices):
    HOURLY_AVG = "hourly_avg", _("Hourly Average")
    HOURLY_MAX = "hourly_max", _("Hourly Maximum")
    HOURLY_MIN = "hourly_min", _("Hourly Minimum")


class CumulativeMeasurementTrigger(Trigger):
    dynamic_metric = models.CharField(max_length=32, choices=DynamicMetric.choices)
    adjustment_factor = models.FloatField(default=0)
    period_days = models.PositiveIntegerField(default=7)
    field_name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        choices=lazy(get_dynamic_fields, list)("measurements", "CumulativeMeasurement"),
    )

    class Meta:
        verbose_name = _("Cumulative Measurement Trigger")
        verbose_name_plural = _("Cumulative Measurement Triggers")

    def __str__(self):
        return f"{self.name}"

    @property
    def active_threshold(self, transductor, target_hour):
        base_threshold = self.get_threshold(transductor, target_hour)
        return base_threshold * (1 + self.adjustment_factor)

    @property
    def deactivate_threshold(self, transductor, target_hour):
        base_threshold = self.get_threshold(transductor, target_hour)
        return base_threshold * (1 - self.adjustment_factor)

    def get_threshold(self, transductor, target_hour):
        measurement_queryset = self.fetch_measurement_data(transductor, target_hour)

        if not measurement_queryset.exists():
            logger.warning("No measurement data found")
            return None

        if self.dynamic_metric == DynamicMetric.HOURLY_AVG:
            return measurement_queryset.aggregate(Avg("value"))["value__avg"]
        elif self.dynamic_metric == DynamicMetric.HOURLY_MAX:
            return measurement_queryset.aggregate(Max("value"))["value__max"]
        elif self.dynamic_metric == DynamicMetric.HOURLY_MIN:
            return measurement_queryset.aggregate(Min("value"))["value__min"]
        elif self.dynamic_metric is None:
            return measurement_queryset.last()

    def fetch_measurement_data(self, transductor, target_hour):
        return CumulativeMeasurement.objects.filter(
            transductor=transductor,
            collection_time__gte=timezone.now() - timedelta(days=self.period_days),
            collection_time__hour=target_hour,
        ).only(self.field_name)

    def clean(self) -> None:
        if self.adjustment_factor < 0 or self.adjustment_factor > 1:
            logger.warning("Adjustment factor must be between 0 and 1")
            raise ValueError("Adjustment factor must be between 0 and 1")

        if self.period_days < 1:
            raise ValueError("Period days must be at least 1")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
