from .api import *
from django.db import models
from django.utils.timezone import datetime
from polymorphic.models import PolymorphicModel
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from polymorphic.models import PolymorphicModel

from .api import *
from campi.models import Campus
from slaves.models import Slave
from groups.models import Group
from django.utils.translation import gettext_lazy as _


class Transductor(PolymorphicModel):
    active = models.BooleanField(
        default=True,
        verbose_name=_('active')
    )
    broken = models.BooleanField(
        default=False,
        verbose_name=_('unreachable')
    )
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_('name'),
        help_text=_('This field is required')
    )

    last_minutely_collection = models.DateTimeField(
        blank=False, 
        null=False,
        default=datetime.now,
        verbose_name=_('last minutely collection')
    )

    last_quarterly_collection = models.DateTimeField(
        blank=False, 
        null=False,
        default=datetime.now,
        verbose_name=_('last quarterly collection')
    )

    last_monthly_collection = models.DateTimeField(
        blank=False, 
        null=False,
        default=datetime.now,
        verbose_name=_('last monthly collection')
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
        ],
        verbose_name=_('IP address'),
        help_text=_('This field is required')
    )

    port = models.IntegerField(
        default=1001,
        help_text=_('This field is required'),
        verbose_name=_('port')
    )

    geolocation_latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('latitude')
    )

    geolocation_longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('longitude')
    )
    serial_number = models.CharField(
        primary_key=False,
        unique=True,
        max_length=8,
        blank=False,
        null=False,
        verbose_name=_('serial number'),
        help_text=_('This field is required')
    )

    firmware_version = models.CharField(
        max_length=20,
        verbose_name=_('firmware version'),
        help_text=_('This field is required')
    )

    creation_date = models.DateTimeField(
        default=datetime.now,
        verbose_name=_('created at')
    )

    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        verbose_name=_('campus'),
        help_text=_('This field is required')
    )

    model = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        verbose_name=_('model'),
        help_text=_('This field is required')
    )

    grouping = models.ManyToManyField(
        Group,
        verbose_name=_('Grouping'),
        help_text=_('This field is required')
    )

    slave_server = models.ForeignKey(
        Slave,
        verbose_name=_('Collection Server'),
        default=None,
        null=True,
        on_delete=models.DO_NOTHING, 
        related_name='transductors'
    )

    id_in_slave = models.IntegerField(
        default=0,
        null=False,
        blank=False
    )

    class Meta:
        abstract = True
        verbose_name = _('Meter')

    def __str__(self):
        raise NotImplementedError

    # def delete(self, *args, **kwargs):
    #     slave = self.slave_server
    #     failed = False

    #     if not kwargs.get('bypass_requests', None):
    #         # try:
    #         response = delete_transductor(self, slave)
    #         # except Exception:
    #             # failed = True

    #         if not self.__is_success_status(response.status_code):
    #             failed = True

    #     if not failed:
    #         super(Transductor, self).delete()

    #     return failed 

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
    class Meta:
        verbose_name = _('Energy meter')

    def __str__(self):
        return 'Energy meter: %s Serial #%s' % (self.name, self.serial_number)

    # There aren't measurements yet
    def get_measurements(self, datetime):
        pass
