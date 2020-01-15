from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import JSONField

from polymorphic.models import PolymorphicModel

from slaves.models import Slave
from transductors.models import EnergyTransductor


class Event(PolymorphicModel):
    """
    Defines a new event object
    """
    settings.USE_TZ = False
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s@%s' % (self.__class__.__name__, self.created_at)

    def save_event(self):
        """
        Saves the event.
        """
        raise NotImplementedError


class VoltageRelatedEvent(Event):
    """
    Defines a new event related to a voltage metric
    """
    measures = JSONField()
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )


class FailedConnectionTransductorEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    @staticmethod
    def save_event(transductor):
        """
        Saves a failed connection event related to a transductor
        """
        new_event = FailedConnectionTransductorEvent()
        new_event.transductor = transductor
        new_event.save()
        return new_event


class FailedConnectionSlaveEvent(Event):
    """
    Defines a new event related to a failed connection with a slave
    """
    slave = models.ForeignKey(
        Slave,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    @staticmethod
    def save_event(slave):
        """
        Saves a failed connection event related to a slave
        """
        new_event = FailedConnectionSlaveEvent()
        new_event.slave = slave
        new_event.save()
        return new_event


class CriticalVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a critical voltage measurement
    """


class PrecariousVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a precarious voltage measurement
    """


class PhaseDropEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a drop on the triphasic voltage measurement
    """


class ConsumptionRelatedEvent(Event):
    """
    Defines a generic event related to consumption event types
    """
    consumption = models.FloatField(default=0.0)


class ConsumptionPeakEvent(ConsumptionRelatedEvent):
    """
    Defines a new event related to a higher peak on transductor measurements
    """


class ConsumptionAboveContract(ConsumptionRelatedEvent):
    """
    Defines a new event related to a moment at the consumptions surpasses the
    consumption contracted
    """
