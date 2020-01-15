from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from transductors.models import EnergyTransductor

'''
    TODO Make get all measurements and list
    transductor models methods
'''


# Create your models here.
class Slave(models.Model):

    ip_address = models.CharField(
        max_length=50,
    )

    port = models.CharField(
        max_length=5,
        default="80"
    )

    location = models.CharField(max_length=50)
    broken = models.BooleanField(default=True)

    transductors = models.ManyToManyField(
        EnergyTransductor, related_name='slave_servers'
    )

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
