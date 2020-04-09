from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

"""
    TODO Make get all measurements and list
    transductor models methods
"""


class Slave(models.Model):

    ip_address = models.CharField(
        max_length=50,
        verbose_name=_('IP address'),
        help_text=_('This field is required')
    )

    port = models.CharField(
        max_length=5,
        default="80",
        verbose_name=_('IP access port')
    )

    name = models.CharField(
        max_length=50,
        verbose_name=_('Location'),
        help_text=_('This field is required'),
        unique=True
    )

    broken = models.BooleanField(
        default=False,
        verbose_name=_('Broken')
    )

    class Meta:
        verbose_name = _('Slave server')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Slave, self).save(*args, **kwargs)

    def add_transductor(self, transductor):
        response = transductor.create_on_server(self)
        if self.__is_success_status(response.status_code):
            self.transductors.add(transductor)
        return response

    def remove_transductor(self, transductor):
        response = transductor.delete_on_server(self)
        if self.__successfully_deleted(response.status_code):
            self.transductors.remove(transductor)
        return response

    def set_broken(self, new_status):
        """
        Set the broken atribute's new status to match the param.
        If toggled to True, creates a failed connection event
        """
        from events.models import FailedConnectionSlaveEvent

        old_status = self.broken

        if old_status is True and new_status is False:
            try:
                related_event = FailedConnectionSlaveEvent.objects.filter(
                    slave=self,
                    ended_at__isnull=True
                ).last()
                related_event.ended_at = timezone.now()
                related_event.save()

            except FailedConnectionSlaveEvent.DoesNotExist as e:
                pass

        elif old_status is False and new_status is True:
            evt = FailedConnectionSlaveEvent()
            evt.save_event(self)

        self.broken = new_status
        self.save(update_fields=['broken'])

    def __is_success_status(self, status):
        if (status is not None) and (200 <= status < 300):
            return True
        else:
            return False

    # FIXME: Improve this
    def __successfully_deleted(self, status):
        if (status is not None) and ((200 <= status < 300) or (status == 404)):
            return True
        else:
            return False
