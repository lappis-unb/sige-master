from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from slaves.models import Slave
from transductors.models import EnergyTransductor


class Event(PolymorphicModel):
    """
    Defines a new event object
    """
    settings.USE_TZ = False
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s@%s' % (self.__class__.__name__, self.created_at)

    def save_event(self):
        """
        Saves the event.
        """
        raise NotImplementedError

    def get_events_from_slave_server(self):
        raise NotImplementedError


class VoltageRelatedEvent(Event):
    """
    Defines a new event related to a voltage metric
    """

    class Meta:
        abstract = True

    phase_a = models.FloatField(default=0)
    phase_b = models.FloatField(default=0)
    phase_c = models.FloatField(default=0)


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
