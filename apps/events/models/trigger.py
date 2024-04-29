import logging
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.events.models import EventType

logger = logging.getLogger("apps")


class EventTrigger(models.Model):
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


class MeasurementType(models.TextChoices):
    INSTANT = "InstantMeasurement", _("Instant Measurement")
    CUMULATIVE = "CumulativeMeasurement", _("Cumulative Measurement")


class MeasurementTrigger(EventTrigger):
    field_name = models.CharField(max_length=100, blank=False, null=False)
    measurement_type = models.CharField(max_length=32, choices=MeasurementType.choices, blank=True)
    upper_limit = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)
    lower_limit = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    operator = models.CharField(max_length=5, choices=CompareOperator.choices)
    debouce_time = models.DurationField(default=timedelta(minutes=1))

    class Meta:
        verbose_name = _("Measurement Trigger")
        verbose_name_plural = _("Measurement Triggers")

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.name = f"{self.measurement_type} - {self.field_name} {self.operator} {self.upper_limit}"
        super().save(*args, **kwargs)

    def get_details(self):
        return {
            "field_name": self.field_name,
            "measurement_type": self.measurement_type,
            "upper_limit": self.upper_limit,
            "lower_limit": self.lower_limit,
            "operator": self.operator,
        }


class CumulativeMeasurementTrigger(MeasurementTrigger):
    class Meta:
        proxy = True

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(measurement_type=MeasurementType.CUMULATIVE)

    objects = Manager()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.measurement_type = MeasurementType.CUMULATIVE
        super().save(*args, **kwargs)


class InstantMeasurementTrigger(MeasurementTrigger):
    class Meta:
        proxy = True

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(measurement_type=MeasurementType.INSTANT)

    objects = Manager()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.measurement_type = MeasurementType.INSTANT
        super().save(*args, **kwargs)
