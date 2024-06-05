import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.measurements.managers import CumulativeMeasurementsManager
from apps.transductors.models import Transductor

logger = logging.getLogger("apps.measurements")


class InstantMeasurement(models.Model):
    frequency_a = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    frequency_b = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    frequency_c = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    frequency_iec = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    voltage_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    voltage_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    voltage_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    current_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    current_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    current_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    active_power_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    active_power_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    active_power_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    total_active_power = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_power_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_power_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_power_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    total_reactive_power = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    apparent_power_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    apparent_power_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    apparent_power_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    total_apparent_power = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    power_factor_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    power_factor_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    power_factor_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    total_power_factor = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dht_voltage_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dht_voltage_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dht_voltage_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dht_current_a = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dht_current_b = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dht_current_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    collection_date = models.DateTimeField(null=True, blank=True)
    transductor = models.ForeignKey(
        Transductor,
        related_name="instant_measurements",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("Instantaneous measurement")
        verbose_name_plural = _("Instantaneous Measurements")
        ordering = ["-collection_date"]
        indexes = [
            models.Index(
                fields=["transductor", "collection_date"],
                name="inst_transductor_date_idx",
            ),
        ]

    def __str__(self):
        return f"{self.transductor.ip_address} - {self.collection_date}"

    def save(self, *args, **kwargs):
        if self.collection_date is None:
            self.collection_date = timezone.now()
        super().save(*args, **kwargs)


class ReferenceMeasurement(models.Model):
    active_consumption = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    active_generated = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_inductive = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_capacitive = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    transductor = models.OneToOneField(
        Transductor,
        related_name="reference_measurement",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("Reference Measurement")
        verbose_name_plural = _("Reference Measurements")

    def __str__(self):
        return f"{self.transductor.ip_address} - {self.updated}"


class CumulativeMeasurement(models.Model):
    active_consumption = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    active_generated = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_inductive = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    reactive_capacitive = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_calculated = models.BooleanField(default=False)
    collection_date = models.DateTimeField(null=True, blank=True)
    transductor = models.ForeignKey(
        Transductor,
        related_name="cumulative_measurements",
        on_delete=models.PROTECT,
    )

    objects = CumulativeMeasurementsManager()

    class Meta:
        verbose_name = _("Cumulative measurement")
        verbose_name_plural = _("Cumulative Measurements")
        ordering = ["-collection_date"]
        indexes = [
            models.Index(
                fields=["transductor", "collection_date"],
                name="cumu_transductor_date_idx",
            ),
        ]

    def __str__(self):
        return f"{self.transductor.ip_address} - {self.collection_date}"

    def save(self, *args, **kwargs):
        if self.collection_date is None:
            self.collection_date = timezone.now()
        super().save(*args, **kwargs)
