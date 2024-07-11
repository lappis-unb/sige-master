import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Max, Min
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.measurements.models import CumulativeMeasurement
from apps.transductors.models import Status, Transductor
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


class TransductorStatusTrigger(Trigger):
    transductors = models.ManyToManyField(Transductor, related_name="status_triggers")
    target_status = models.IntegerField(choices=Status.choices)
    threshold_time = models.DurationField(default=timedelta(hours=1))

    class Meta:
        verbose_name = _("Transductor Status Trigger")
        verbose_name_plural = _("Transductor Status Triggers")

    def __str__(self):
        return f"{self.name} - {self.target_status}"


class InstantMeasurementTrigger(Trigger):
    lower_threshold = models.FloatField(blank=True, null=True)
    upper_threshold = models.FloatField(blank=True, null=True)
    field_name = models.CharField(max_length=64, blank=False, null=False)

    @classmethod
    def init_choices(cls):
        cls._meta.get_field("field_name").choices = get_dynamic_fields("measurements", "InstantMeasurement")

    class Meta:
        verbose_name = _("Instant Measurement Trigger")
        verbose_name_plural = _("Instant Measurement Triggers")

    def __str__(self):
        return f"{self.name} - {self.field_name}"

    def clean(self) -> None:
        lower_threshold = self.lower_threshold if self.lower_threshold is not None else float("-inf")
        upper_threshold = self.upper_threshold if self.upper_threshold is not None else float("inf")

        if lower_threshold >= upper_threshold:
            logger.error("lower_threshold must be less than upper_threshold")
            raise ValidationError("lower_threshold must be less than upper_threshold")

        overlapping = InstantMeasurementTrigger.objects.filter(
            field_name=self.field_name,
            lower_threshold__lte=self.upper_threshold,
            upper_threshold__gte=self.lower_threshold,
        ).exclude(pk=self.pk)

        list_overlapping = overlapping.values_list("lower_threshold", "upper_threshold")
        dict_overlapping = {f"{lower} <= value < {upper}" for lower, upper in list_overlapping}
        if overlapping.exists():
            logger.error(f"Overlapping triggers found: {dict_overlapping}")
            raise ValidationError(f"Overlapping triggers found: {dict_overlapping}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class DynamicMetric(models.TextChoices):
    HOURLY_AVG = "hourly_avg", _("Hourly Average")
    HOURLY_MAX = "hourly_max", _("Hourly Maximum")
    HOURLY_MIN = "hourly_min", _("Hourly Minimum")


class CumulativeMeasurementTrigger(Trigger):
    dynamic_metric = models.CharField(max_length=32, choices=DynamicMetric.choices)
    lower_threshold_percent = models.FloatField(default=0)
    upper_threshold_percent = models.FloatField(default=0)
    period_days = models.PositiveIntegerField(default=7)
    field_name = models.CharField(max_length=64, blank=False, null=False)

    @classmethod
    def init_choices(cls):
        cls._meta.get_field("field_name").choices = get_dynamic_fields("measurements", "CumulativeMeasurement")

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
            collection_date__hour=target_hour,
        ).only(self.field_name)

    def clean(self):
        if not (0 <= self.lower_threshold_percent <= 1):
            logger.error("lower_threshold_percent must be between 0 and 1")
            raise ValidationError("lower_threshold_percent must be between 0 and 1")

        if not (0 <= self.upper_threshold_percent <= 1):
            logger.error("upper_threshold_percent must be between 0 and 1")
            raise ValidationError("upper_threshold_percent must be between 0 and 1")

        if self.period_days < 1:
            logger.error("Period days must be at least 1")
            raise ValidationError("Period days must be at least 1")

        if self.lower_threshold_percent >= self.upper_threshold_percent:
            logger.error("lower_threshold_percent must be less than upper_threshold_percent")
            raise ValidationError("lower_threshold_percent must be less than upper_threshold_percent")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
