from .api import *
from django.db import models
from datetime import datetime
from polymorphic.models import PolymorphicModel
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Transductor(PolymorphicModel):
    serial_number = models.CharField(
        primary_key=True,
        unique=True,
        max_length=8,
        blank=False,
        null=False
    )
    ip_address = models.CharField(
        max_length=15,
        unique=True,
        default='0.0.0.0',
        validators=[
            RegexValidator(
                regex='^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
                message='Incorrect IP address format',
                code='invalid_ip_address'
            ),
        ]
    )
    physical_location = models.CharField(max_length=256, blank=True)
    geolocation_latitude = models.FloatField(null=True, blank=True)
    geolocation_longitude = models.FloatField(null=True, blank=True)
    firmware_version = models.CharField(max_length=20)
    name = models.CharField(max_length=256, blank=True)
    broken = models.BooleanField(default=True)
    active = models.BooleanField(default=False)
    creation_date = models.DateTimeField(null=True, blank=True)
    calibration_date = models.DateTimeField(null=True, blank=True)

    model = models.CharField(
        max_length=256,
        blank=False,
        null=False,
    )

    class Meta:
        abstract = True

    def __str__(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Transductor, self).save()

    def update(self, *args, **kwargs):
        self.full_clean()

        failed = False

        for slave in self.slave_servers.all():
            if not kwargs.get('bypass_requests', None):
                response = update_transductor(self, slave)
                if not self.__is_success_status(response.status_code):
                    failed = True

        if not failed:
            super(Transductor, self).save()
        else:
            # FIXME: Raise exception
            print("Couldn't update this transductor in all Slave Servers")

    def delete(self, *args, **kwargs):
        self.active = False

        failed = False
        for slave in self.slave_servers.all():
            if not kwargs.get('bypass_requests', None):
                response = slave.remove_transductor(self)
                if not self.__successfully_deleted(response.status_code):
                    failed = True

        if not failed:
            self.full_clean()
            super(Transductor, self).delete()
        else:
            # FIXME: Raise exception
            print("Couldn't delete this transductor in all Slave Servers")

    def get_measurements(self, datetime):
        raise NotImplementedError

    def activate(self):
        if(len(self.slave_servers.all()) > 0):
            self.active = True
        else:
            self.active = False

    def get_active_status(self):
        self.activate()
        return self.active

    def create_on_server(self, slave_server):
        return create_transductor(self, slave_server)

    def delete_on_server(self, slave_server):
        return delete_transductor(self, slave_server)

    def collect_broken_status(self):
        return self.broken

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


class EnergyTransductor(Transductor):
    def __str__(self):
        return 'Energy Transductor: '
        + self.name
        + ' Serial number #'
        + self.serial_number

    # There aren't measurements yet
    def get_measurements(self, datetime):
        pass
