from django.db import models


class TransductorModel(models.Model):
    """
    Class responsible to define a transductor model which contains
    crucial informations about the transductor itself.

    Attributes:
        name (str): The factory name.
        transport_protocol (str): The transport protocol.
        serial_protocol (str): The serial protocol.
    """

    name = models.CharField(max_length=50, unique=True)
    serial_protocol = models.CharField(max_length=50)
    transport_protocol = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(TransductorModel, self).save(*args, **kwargs)
