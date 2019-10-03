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
        max_length=9,
        unique=True,
        primary_key=True
    )

    name = models.CharField(max_length=50, unique=True)
    serial_protocol = models.CharField(max_length=50)
    transport_protocol = models.CharField(max_length=50)
    minutely_register_addresses = ArrayField(ArrayField(models.IntegerField()),
                                             default=None)
    quarterly_register_addresses = ArrayField(ArrayField(models.IntegerField()),
                                              default=None)
    monthly_register_addresses = ArrayField(ArrayField(models.IntegerField()),
                                            default=None)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        if not kwargs.get('bypass_requests', None):
            from slaves.models import Slave
            for slave in Slave.objects.all():
                create_transductor_model(self, slave)

        super(TransductorModel, self).save()

    def update(self, *args, **kwargs):
        self.full_clean()
        failed = False

        if not kwargs.get('bypass_requests', None):
            from slaves.models import Slave
            for slave in Slave.objects.all():
                response = update_transductor_model(self, slave)
                if not self.__is_success_status(response.status_code):
                    failed = True

        if not failed:
            super(TransductorModel, self).save()
        else:
            # FIXME: Raise exception
            print("Couldn't update this transductor model in all Slave Servers")

    def delete(self, *args, **kwargs):
        self.full_clean()
        failed = False

        if not kwargs.get('bypass_requests', None):
            from slaves.models import Slave
            for slave in Slave.objects.all():
                response = delete_transductor_model(self, slave)
                if not self.__successfully_deleted(response.status_code):
                    failed = True

        if not failed:
            super(TransductorModel, self).delete()
        else:
            # FIXME: Raise exception
            print("Couldn't delete this transductor model in all Slave Servers")

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
