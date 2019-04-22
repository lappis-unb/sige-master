from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator

#TODO Make get all measurements and list transductor models methods


# Create your models here.
class Slave(models.Model):

    ip_validator = RegexValidator(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', 'Incorrect IP address format')

    ip_address = models.CharField(
        max_length=15,
        unique=True,
        validators=[ip_validator],
        default="0.0.0.0"
    )
    location = models.CharField(default="", max_length=50)
    broken = models.BooleanField(default=True)

    def __str__(self):
        return self.ip_address

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Slave, self).save(*args, **kwargs)