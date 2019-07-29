from .api import *
from django.db import models
from django.contrib.postgres.fields import ArrayField


class TransductorModel(models.Model):
    """
    Class responsible to define a transductor model which contains
    crucial informations about the transductor itself.

    Attributes:
        name (str): The factory name.
        transport_protocol (str): The transport protocol.
        serial_protocol (str): The serial protocol.
    """

    model_code = models.CharField(
        max_length=10,
        unique=True,
        primary_key=True
    )

    name = models.CharField(max_length=50, unique=True)
    serial_protocol = models.CharField(max_length=50)
    transport_protocol = models.CharField(max_length=50)
    minutely_register_addresses = ArrayField(ArrayField(models.IntegerField()), default = None)
    quarterly_register_addresses = ArrayField(ArrayField(models.IntegerField()), default = None)
    monthly_register_addresses = ArrayField(ArrayField(models.IntegerField()), default = None)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if(create_transductor_model(self).status_code == 201):
            self.full_clean()
            super(TransductorModel, self).save(*args, **kwargs)
