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

    ip_validator = RegexValidator(
        r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
        'Incorrect IP address format'
    )

    ip_address = models.CharField(
        max_length=15,
        unique=True,
        validators=[ip_validator],
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
        self.transductors.add(transductor)

    def remove_transductor(self, transductor):
        self.transductors.remove(transductor)
