from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from transductors.models import EnergyTransductor

'''
    TODO Make get all measurements and list
    transductor models methods
'''


class Slave(models.Model):

    ip_address = models.CharField(
        max_length=50,
        verbose_name=_('IP address')
    )

    port = models.CharField(
        max_length=5,
        default="80",
        verbose_name=_('IP access port')
    )

    location = models.CharField(
        max_length=50,
        verbose_name=_('Location')
    )

    broken = models.BooleanField(
        default=False,
        verbose_name=_('Broken')
    )

    transductors = models.ManyToManyField(
        EnergyTransductor,
        related_name='slave_servers',
        verbose_name=_('Meters')
    )

    class Meta:
        verbose_name = _('Slave server')

    def __str__(self):
        return self.ip_address

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

    # FIXME: Improve this
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
