from django.db import models
from datetime import datetime
from polymorphic.models import PolymorphicModel
from transductor_models.models import TransductorModel

# There aren't slave servers yet
# from slave_servers.models import SlaveServer


class Transductor(PolymorphicModel):
    serial_number = models.CharField(
        primary_key=True,
        unique=True,
        max_length=8,
        blank=False,
        null=False
    )
    ip_address = models.CharField(max_length=15, blank=False, default='0.0.0.0')
    location = models.CharField(max_length=256, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    name = models.CharField(max_length=256, blank=True)
    broken = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(null=True)
    calibration_date = models.DateTimeField(null=True)
    last_data_collection = models.DateTimeField(null=True)

    model = models.ForeignKey(
        TransductorModel,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='transductors'
    )

    # There aren't slave servers yet
    # slave_server = models.ManyToManyFields(
    #     SlaveServer, related_name='transductors'
    # )

    class Meta:
        abstract = True

    def __str__(self):
        raise NotImplementedError

    def collect_broken_status(self):
        raise NotImplementedError

    def get_measurements(self, datetime):
        raise NotImplementedError


class EnergyTransductor(Transductor):
    def __str__(self):
        return 'Transductor: '
        + self.name
        + ' Serial number #'
        + self.serial_number

    def collect_broken_status(self):
        return self.broken

    # There aren't measurements yet
    def get_measurements(self, datetime):
        pass
