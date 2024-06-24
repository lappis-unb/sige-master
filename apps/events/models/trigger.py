import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Max, Min
from django.utils import timezone
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.measurements.models import CumulativeMeasurement
from apps.utils.helpers import get_dynamic_fields

logger = logging.getLogger("apps")


class CategoryTrigger(models.IntegerChoices):
    VOLTAGE = 1, _("Voltage")
    CONNECTION = 2, _("Connection")
    CONSUMPTION = 3, _("Consumption")
    GENERATION = 4, _("Generation")
    MEASUREMENT = 5, _("Measurement")
    OTHER = 6, _("Other")


class SeverityTrigger(models.IntegerChoices):
    LOW = 1, _("Low")
    MEDIUM = 2, _("Medium")
    HIGH = 3, _("High")
    CRITICAL = 4, _("Critical")


class Trigger(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    severity = models.IntegerField(choices=SeverityTrigger.choices)
    category = models.IntegerField(choices=CategoryTrigger.choices)
    notification_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class InstantMeasurementTrigger(Trigger):
    lower_threshold = models.FloatField(blank=True, null=True)
    upper_threshold = models.FloatField(blank=True, null=True)
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
        return f"{self.name} - {self.field_name}"


class DynamicMetric(models.TextChoices):
    HOURLY_AVG = "hourly_avg", _("Hourly Average")
    HOURLY_MAX = "hourly_max", _("Hourly Maximum")
    HOURLY_MIN = "hourly_min", _("Hourly Minimum")


class CumulativeMeasurementTrigger(Trigger):
    dynamic_metric = models.CharField(max_length=32, choices=DynamicMetric.choices)
    lower_threshold_percent = models.FloatField(default=0)
    upper_threshold_percent = models.FloatField(default=0)
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
        return f"{self.name} - {self.field_name}"

    def calculate_threshold(self, base_value, threshold_percent):
        return float(base_value) * threshold_percent

    def get_upper_threshold(self, transductor, collection_date):
        base_value = self.calculate_metric(transductor, collection_date)
        return self.calculate_threshold(base_value, self.upper_threshold_percent)

    def get_lower_threshold(self, transductor, collection_date):
        base_value = self.calculate_metric(transductor, collection_date)
        return self.calculate_threshold(base_value, self.lower_threshold_percent)

    def calculate_metric(self, transductor, collection_date):
        local_collection_date = collection_date.astimezone(timezone.get_current_timezone())
        target_hour = local_collection_date.hour
        target_hour = 12
        measurement_queryset = self.fetch_measurement_data(transductor, target_hour)

        if not measurement_queryset.exists():
            logger.warning("No measurement data found")
            return None

        if self.dynamic_metric == DynamicMetric.HOURLY_AVG:
            return measurement_queryset.aggregate(Avg(self.field_name))[f"{self.field_name}__avg"]
        elif self.dynamic_metric == DynamicMetric.HOURLY_MAX:
            return measurement_queryset.aggregate(Max(self.field_name))[f"{self.field_name}__max"]
        elif self.dynamic_metric == DynamicMetric.HOURLY_MIN:
            return measurement_queryset.aggregate(Min(self.field_name))[f"{self.field_name}_min"]
        elif self.dynamic_metric is None:
            return measurement_queryset.last()

    def fetch_measurement_data(self, transductor, target_hour):
        return CumulativeMeasurement.objects.filter(
            transductor=transductor,
            collection_date__gte=timezone.now() - timedelta(days=self.period_days),
            collection_date__hour=target_hour,  # validar se esta em UTC
        ).only(self.field_name)

    def clean(self):
        errors = []
        if not (0 <= self.lower_threshold_percent <= 1):
            error_msg = "lower_threshold_percent must be between 0 and 1"
            logger.warning(error_msg)
            errors.append(ValidationError(error_msg))

        if not (0 <= self.upper_threshold_percent <= 1):
            error_msg = "upper_threshold_percent must be between 0 and 1"
            logger.warning(error_msg)
            errors.append(ValidationError(error_msg))

        if self.period_days < 1:
            error_msg = "Period days must be at least 1"
            logger.warning(error_msg)
            errors.append(ValidationError(error_msg))

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
