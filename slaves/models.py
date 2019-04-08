from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator

#TODO Make get all measurements and list transductor models methods


# Create your models here.
class Slave(models.Model):
    ip_address = models.CharField(
        max_length=15,
        unique=True,
        default="0.0.0.0",
        validators=[
            RegexValidator(
                regex='^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
                message='Incorrect IP address format',
                code='invalid_ip_address'
            ),
        ]
    )
    location = models.CharField(default="", max_length=50)
    transductor_list = ArrayField(models.IntegerField(default=0))

    def __str__():
        return self.name
