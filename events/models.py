from django.db import models
# from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _

from polymorphic.models import PolymorphicModel

from slaves.models import Slave
from transductors.models import EnergyTransductor

from fcm_django.fcm import fcm_send_topic_message

TOPIC_NAME = 'ALL'


class Event(PolymorphicModel):
    """
    Defines a new event object
    """
    # settings.USE_TZ = False
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('ended at')
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('created at'),
    )
    data = JSONField(
        default=dict,
        verbose_name=_('details'),
        help_text=_('This field is required')
    )

    class Meta:
        verbose_name = _('event')

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

    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name=_('meter'),
        help_text=_('This field is required')
    )

    class Meta:
        verbose_name = _('voltage related')

    def save_event(self, transductor, event_dict):
        """
        Saves a failed connection event related to a transductor
        """
        self.transductor = transductor
        self.data = event_dict['data']
        self.created_at = event_dict['created_at']
        self.ended_at = event_dict['ended_at']
        self.save()

        body = self.transductor.name + '\n'
        counter = 0

        if self.__class__.__name__ == 'PhaseDropEvent':
            for key, value in self.data.items():
                body += 'Fase ' + key[-1].upper()
                counter += 1
                if counter < len(self.data):
                    body += ', '
        else:
            for key, value in self.data.items():
                body += key[-1].upper() + ' - ' + str(value) + 'V'
                counter += 1
                if counter < len(self.data):
                    body += ', '

        fcm_send_topic_message(
            topic_name=TOPIC_NAME,
            data_message={
                'title': str(self._meta.verbose_name).capitalize(),
                'body': body,
                'transducer': self.pk
            }
        )
        return self


class FailedConnectionTransductorEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name=_('meter'),
        help_text=_('This field is required')
    )

    class Meta:
        verbose_name = _('failed connection with meter')

    def save_event(self, transductor, event_dict):
        """
        Saves a failed connection event related to a transductor
        """
        self.transductor = transductor
        self.data = event_dict['data']
        self.created_at = event_dict['created_at']
        self.ended_at = event_dict['ended_at']
        self.save()
        body = self.transductor.name

        fcm_send_topic_message(
            topic_name=TOPIC_NAME,
            data_message={
                'title': str(self._meta.verbose_name).capitalize(),
                'body': body,
                'transducer': self.pk
            }
        )
        return self


class FailedConnectionSlaveEvent(Event):
    """
    Defines a new event related to a failed connection with a slave
    """
    slave = models.ForeignKey(
        Slave,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name=_('slave'),
        help_text=_('This field is required')
    )

    class Meta:
        verbose_name = _('failed connection with slave server')

    def save_event(self, slave):
        """
        Saves a failed connection event related to a slave
        """
        self.slave = slave
        self.data = {}
        self.created_at = timezone.now()
        self.ended_at = None
        self.save()
        return self


class CriticalVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a critical voltage measurement
    """

    class Meta:
        verbose_name = _('critical voltage')


class PrecariousVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a precarious voltage measurement
    """

    class Meta:
        verbose_name = _('precarious voltage')


class PhaseDropEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a drop on the triphasic voltage measurement
    """

    class Meta:
        verbose_name = _('phase drop')


class ConsumptionRelatedEvent(Event):
    """
    Defines a generic event related to consumption event types
    """
    consumption = models.FloatField(
        default=0.0,
        verbose_name=_('consumption related')
    )


class ConsumptionPeakEvent(ConsumptionRelatedEvent):
    """
    Defines a new event related to a higher peak on transductor measurements
    """

    class Meta:
        verbose_name = _('consumption peak')


class ConsumptionAboveContract(ConsumptionRelatedEvent):
    """
    Defines a new event related to a moment at the consumptions surpasses the
    consumption contracted
    """

    class Meta:
        verbose_name = _('consumption above contracted threshold')
