import logging

from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.locations.models import GeographicLocation
from apps.organizations.models import Entity
from apps.transductors.managers import TransductorsManager
from apps.transductors.utils import upload_directory_path

logger = logging.getLogger("apps")


class TransductorModel(models.Model):
    class Protocol(models.IntegerChoices):
        TCP = 1, _("Modbus TCP")  # TCP Socket 5020
        UDP = 2, _("Modbus UDP")  # UDP Socket 5020
        RTU = 3, _("Modbus Serial RTU")  # Serial RTU /dev/ptyp0
        TLS = 4, _("TLS")  # TLS 5020

    class RegisterReadFuction(models.IntegerChoices):
        RHR = 1, _("Read Holding Registers")
        RIR = 2, _("Read Input Registers")

    name = models.CharField(max_length=64, unique=True)
    manufacturer = models.CharField(max_length=64)
    protocol = models.IntegerField(choices=Protocol.choices)
    read_function = models.IntegerField(choices=RegisterReadFuction.choices)
    modbus_addr_id = models.PositiveSmallIntegerField(blank=True, default=1)
    max_block_size = models.PositiveSmallIntegerField(blank=True, default=100)
    base_address = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    memory_map_file = models.FileField(upload_to=upload_directory_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "modelo"
        verbose_name_plural = "modelos"

    def __str__(self):
        return f"{self.manufacturer} - {self.name}"


class Transductor(models.Model):
    ip_address = models.GenericIPAddressField(protocol="IPv4")
    port = models.PositiveIntegerField(default=502)
    firmware_version = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=255, blank=True)
    is_generator = models.BooleanField(default=True)
    installation_date = models.DateTimeField(default=timezone.now)
    serial_number = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        unique=True,
    )
    geo_location = models.OneToOneField(
        GeographicLocation,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="transductor",
    )
    model = models.ForeignKey(
        TransductorModel,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )
    located = models.ForeignKey(
        Entity,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="transductors",
    )

    objects = TransductorsManager()

    @property
    def memory_map(self):
        return self.model.memory_map

    @property
    def current_status(self):
        return self.status_history.filter(end_time__isnull=True).first()

    @property
    def uptime(self):
        if self.current_status.status == Status.ACTIVE:
            uptime = timezone.now() - self.current_status.start_time
            return uptime.total_seconds() / 60
        return 0

    class Meta:
        ordering = ("model", "ip_address")
        verbose_name = "transductor"
        verbose_name_plural = "transductores"

    def __str__(self) -> str:
        return f"{self.model.name} - {self.ip_address}"

    def set_broken(self, notes=None):
        return self.set_status(Status.BROKEN, notes)

    def set_status(self, new_status, notes=None):
        if new_status not in [status.value for status in Status]:
            logger.error(f"Invalid status provided: {new_status}")
            raise ValueError("Invalid status provided")

        return StatusHistory.objects.create(
            transductor=self,
            status=new_status,
            notes=f"Transductor status changed to {Status(new_status).name}. {notes or ''}.",
        )


class Status(models.IntegerChoices):
    ACTIVE = 1, "Active"
    BROKEN = 2, "Broken"
    DISABLED = 3, "Disabled"
    MAINTENANCE = 4, "Maintenance"
    TRANSFERRED = 5, "Transferred"
    OTHER = 6, "Other"


class StatusHistory(models.Model):
    status = models.IntegerField(choices=Status.choices)
    notes = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.GeneratedField(
        expression=F("end_time") - F("start_time"),
        output_field=models.DurationField(),
        db_persist=True,
    )
    transductor = models.ForeignKey(
        Transductor,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="status_history",
    )

    class Meta:
        verbose_name = _("transductor status")
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.get_status_display()}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                logger.info(f"Closing status {self.transductor} - {self.get_status_display()}")
            elif self.manage_status_transition():
                logger.info(f"Creating new status {self.transductor} - {self.get_status_display()}")
            else:
                return
            super().save(*args, **kwargs)

    def manage_status_transition(self):
        current_status = self.get_open_status()
        if current_status and current_status.status == self.status:
            logger.warning(f"{self.transductor} - Status already in {Status(self.status).name}. Skipping save!.")
            return False
        if current_status:
            current_status.close_status()
        return True

    def close_status(self):
        if self.end_time is not None:
            logger.error(f"{self.transductor} - Status is already closed.")
            raise ValueError("Cannot close a status that is already closed")

        self.end_time = timezone.now()
        self.save(update_fields=["end_time"])

    def get_open_status(self):
        open_status = self.transductor.status_history.filter(end_time__isnull=True)

        if open_status.count() > 1:
            logger.error(f"{self.transductor} - Multiple open statuses found.")
            logger.info(f"Closing all open statuses: {open_status.count()} for {self.transductor}")
            open_status.exclude(pk=self.pk).update(end_time=timezone.now())

        return open_status.first() if open_status.exists() else None
