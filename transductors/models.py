from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from campi.models import Campus
from groups.models import Group
from slaves.models import Slave

from transductors.api import delete_transductor, update_transductor, create_transductor


class Transductor(models.Model):
    name = models.CharField(max_length=256, blank=True, verbose_name=_("name"))
    model = models.CharField(max_length=256, verbose_name=_("model"))
    firmware_version = models.CharField(max_length=20, verbose_name=_("firmware version"))
    ip_address = models.GenericIPAddressField(unique=True, protocol="IPv4")
    port = models.PositiveIntegerField(default=1001, verbose_name=_("port"))
    geolocation_latitude = models.FloatField(default=0, blank=True, verbose_name=_("latitude"))
    geolocation_longitude = models.FloatField(default=0, blank=True, verbose_name=_("longitude"))
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, verbose_name=_("campus"))
    grouping = models.ManyToManyField(Group, verbose_name=_("Grouping"), blank=True)
    last_minutely_collection = models.DateTimeField(default=timezone.now)
    last_quarterly_collection = models.DateTimeField(default=timezone.now)
    last_monthly_collection = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True, verbose_name=_("active"))
    broken = models.BooleanField(default=False, verbose_name=_("broken"))
    pending_sync = models.BooleanField(default=False)
    pending_deletion = models.BooleanField(default=False)
    creation_date = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))
    power = models.IntegerField(default=0, verbose_name=_("power"))
    is_generator = models.BooleanField(default=False, verbose_name=_("is generator"))
    history = models.TextField(blank=True, verbose_name=_("history"))
    slave_server = models.ForeignKey(
        Slave,
        verbose_name=_("Collection Server"),
        default=None,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="transductors",
    )
    serial_number = models.CharField(
        primary_key=False,
        unique=True,
        max_length=8,
        verbose_name=_("serial number"),
        validators=[MinLengthValidator(1)],
    )

    class Meta:
        abstract = True
        verbose_name = _("Meter")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Transductor, self).save()

    def get_measurements(self, datetime):
        raise NotImplementedError

    def activate(self):
        if len(self.slave_servers.all()) > 0:
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
        verbose_name = _("Energy meter")

    def __str__(self):
        return f"{self.name} - {self.ip_address}"

    # There aren't measurements yet
    def get_measurements(self, datetime):
        pass
    