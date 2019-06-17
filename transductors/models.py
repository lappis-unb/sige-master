from django.db import models
from datetime import datetime
from polymorphic.models import PolymorphicModel
from transductor_models.models import TransductorModel
from django.core.exceptions import ValidationError


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
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    name = models.CharField(max_length=256, blank=True)
    broken = models.BooleanField(default=True)
    active = models.BooleanField(default=False)
    creation_date = models.DateTimeField(null=True, blank=True)
    calibration_date = models.DateTimeField(null=True, blank=True)
    last_data_collection = models.DateTimeField(null=True, blank=True)

    model = models.ForeignKey(
        TransductorModel,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='transductors'
    )

    class Meta:
        abstract = True

    def __str__(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Transductor, self).save(*args, **kwargs)

    def get_measurements(self, datetime):
        raise NotImplementedError

    def activate(self):
        if(len(self.slave_servers.all()) > 0):
            print("Successfully activated!")
            self.active = True
        else:
            print("Can't activate a transductor with no slave associated!")
            self.active = False

    def get_active_status(self):
        self.activate()
        return self.active

    def collect_broken_status(self):
        return self.broken


class EnergyTransductor(Transductor):
    def __str__(self):
        return 'Transductor: '
        + self.name
        + ' Serial number #'
        + self.serial_number

    # There aren't measurements yet
    def get_measurements(self, datetime):
        pass
