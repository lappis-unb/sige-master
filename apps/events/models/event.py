import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# from apps.events.models import EventTrigger
from apps.transductors.models import Transductor

logger = logging.getLogger("apps")


class CategoryEvent(models.IntegerChoices):
    VOLTAGE = 1, _("Voltage")
    CONNECTION = 2, _("Connection")
    CONSUMPTION = 3, _("Consumption")
    GENERATION = 4, _("Generation")
    MEASUREMENT = 5, _("Measurement")
    OTHER = 6, _("Other")


class SeverityEvent(models.IntegerChoices):
    LOW = 1, _("Low")
    MEDIUM = 2, _("Medium")
    HIGH = 3, _("High")
    CRITICAL = 4, _("Critical")


class EventType(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=3)
    severity = models.IntegerField(choices=SeverityEvent.choices)
    category = models.IntegerField(choices=CategoryEvent.choices)

    class Meta:
        verbose_name = _("Event Type")
        verbose_name_plural = _("Event Types")

    def __str__(self):
        return f"{self.name} ({self.code})"


class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    transductor = models.ForeignKey(
        Transductor,
        on_delete=models.CASCADE,
        related_name="events_transductor",
    )
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE,
        related_name="events_type",
    )
    measurement_trigger = models.ForeignKey(
        "events.EventTrigger",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events_trigger",
    )

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"

    def close_event(self):
        if not self.is_active:
            raise ValidationError(_("Event is already closed."))
        self.ended_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["ended_at", "is_active"])

    def has_active_event(self):
        return Event.objects.filter(
            transductor=self.transductor,
            measurement_trigger=self.measurement_trigger,
            is_active=True,
        ).exists()

    def save(self, *args, **kwargs):
        if not self.pk and self.has_active_event():
            raise ValidationError("An active event for this transductor and trigger already exists.")
        super().save(*args, **kwargs)
