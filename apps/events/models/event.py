import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.transductors.models import Transductor

logger = logging.getLogger("apps")


class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    transductor = models.ForeignKey(
        Transductor,
        on_delete=models.CASCADE,
        related_name="events_transductor",
    )
    trigger = models.ForeignKey(
        "events.Trigger",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events_trigger",
    )

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return f"{self.name} - {self.created_at}"

    @property
    def name(self):
        return self.trigger.name

    @property
    def severity(self):
        return self.trigger.severity

    @property
    def category(self):
        return self.trigger.category

    def close_event(self):
        if not self.is_active:
            raise ValidationError(_("Event is already closed."))
        self.ended_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["ended_at", "is_active"])

    def has_active_event(self):
        return Event.objects.filter(
            transductor=self.transductor,
            trigger=self.trigger,
            is_active=True,
        ).exists()

    def save(self, *args, **kwargs):
        if not self.pk and self.has_active_event():
            raise ValidationError("An active event for this transductor and trigger already exists.")
        super().save(*args, **kwargs)
