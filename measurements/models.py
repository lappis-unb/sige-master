from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from transductors.models import EnergyTransductor


class Tax(models.Model):
    value_peak = models.FloatField(default=None, null=True)
    value_off_peak = models.FloatField(default=None, null=True)
    registration_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Tax")


class Measurement(models.Model):
    collection_date = models.DateTimeField(default=timezone.now)
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        verbose_name=_("Energy meter"),
    )

    def __str__(self):
        return f"{self.collection_date} - {self.transductor}"

    class Meta:
        abstract = True
        verbose_name = _("Measurement")


class MinutelyMeasurement(Measurement):
    frequency_a = models.FloatField(default=None, null=True, blank=True)
    voltage_a = models.FloatField(default=None, null=True)
    voltage_b = models.FloatField(default=None, null=True)
    voltage_c = models.FloatField(default=None, null=True)
    current_a = models.FloatField(default=None, null=True)
    current_b = models.FloatField(default=None, null=True)
    current_c = models.FloatField(default=None, null=True)
    active_power_a = models.FloatField(default=None, null=True)
    active_power_b = models.FloatField(default=None, null=True)
    active_power_c = models.FloatField(default=None, null=True)
    total_active_power = models.FloatField(default=None, null=True)
    reactive_power_a = models.FloatField(default=None, null=True)
    reactive_power_b = models.FloatField(default=None, null=True)
    reactive_power_c = models.FloatField(default=None, null=True)
    total_reactive_power = models.FloatField(default=None, null=True)
    apparent_power_a = models.FloatField(default=None, null=True)
    apparent_power_b = models.FloatField(default=None, null=True)
    apparent_power_c = models.FloatField(default=None, null=True)
    total_apparent_power = models.FloatField(default=None, null=True)
    power_factor_a = models.FloatField(default=None, null=True)
    power_factor_b = models.FloatField(default=None, null=True)
    power_factor_c = models.FloatField(default=None, null=True)
    total_power_factor = models.FloatField(default=None, null=True)
    dht_voltage_a = models.FloatField(default=None, null=True)
    dht_voltage_b = models.FloatField(default=None, null=True)
    dht_voltage_c = models.FloatField(default=None, null=True)
    dht_current_a = models.FloatField(default=None, null=True)
    dht_current_b = models.FloatField(default=None, null=True)
    dht_current_c = models.FloatField(default=None, null=True)

    class Meta:
        verbose_name = _("Minutely measurement")
        verbose_name_plural = _("Minutely Measurements")


class QuarterlyMeasurement(Measurement):
    generated_energy_peak_time = models.FloatField(default=None, null=True)
    generated_energy_off_peak_time = models.FloatField(default=None, null=True)
    consumption_peak_time = models.FloatField(default=None, null=True)
    consumption_off_peak_time = models.FloatField(default=None, null=True)
    inductive_power_peak_time = models.FloatField(default=None, null=True)
    inductive_power_off_peak_time = models.FloatField(default=None, null=True)
    capacitive_power_peak_time = models.FloatField(default=None, null=True)
    capacitive_power_off_peak_time = models.FloatField(default=None, null=True)
    is_calculated = models.BooleanField(default=False)
    tax = models.ForeignKey(Tax, null=True, on_delete=models.SET_NULL)  # TODO: Verificar se é necessário

    class Meta:
        verbose_name = _("Quartely measurement")
        verbose_name_plural = _("Quarterly Measurements")

    def __str__(self):
        return f"{self.collection_date} - {self.transductor}"


class MonthlyMeasurement(Measurement):
    generated_energy_peak_time = models.FloatField(default=None, null=True)
    generated_energy_off_peak_time = models.FloatField(default=None, null=True)
    consumption_peak_time = models.FloatField(default=None, null=True)
    consumption_off_peak_time = models.FloatField(default=None, null=True)
    inductive_power_peak_time = models.FloatField(default=None, null=True)
    inductive_power_off_peak_time = models.FloatField(default=None, null=True)
    capacitive_power_peak_time = models.FloatField(default=None, null=True)
    capacitive_power_off_peak_time = models.FloatField(default=None, null=True)
    active_max_power_peak_time = models.FloatField(default=None, null=True)
    active_max_power_off_peak_time = models.FloatField(default=None, null=True)
    reactive_max_power_peak_time = models.FloatField(default=None, null=True)
    reactive_max_power_off_peak_time = models.FloatField(default=None, null=True)

    # TODO O slave não está mais fornecendo esses atributos (validar e deletar)
    # active_max_power_list_peak = ArrayField(models.FloatField(), default=None)
    # active_max_power_list_peak_time = ArrayField(models.DateTimeField(), default=None)
    # active_max_power_list_off_peak = ArrayField(models.FloatField(), default=None)
    # active_max_power_list_off_peak_time = ArrayField(models.DateTimeField(), default=None)
    # reactive_max_power_list_peak = ArrayField(models.FloatField(), default=None)
    # reactive_max_power_list_peak_time = ArrayField(models.DateTimeField(), default=None)
    # reactive_max_power_list_off_peak = ArrayField(models.FloatField(), default=None)
    # reactive_max_power_list_off_peak_time = ArrayField(models.DateTimeField(), default=None)

    class Meta:
        verbose_name = _("Monthly measurement")
        verbose_name_plural = _("Minutely Measurements")

    def __str__(self):
        return f"{self.collection_date} - {self.transductor}"


# TODO: Verificar se é necessário duplicar dados da model MinutelyMeasurement
class RealTimeMeasurement(Measurement):
    voltage_a = models.FloatField(default=None, null=True, verbose_name=_("Voltage on phase A"))
    voltage_b = models.FloatField(default=None, null=True, verbose_name=_("Voltage on phase B"))
    voltage_c = models.FloatField(default=None, null=True, verbose_name=_("Voltage on phase C"))
    current_a = models.FloatField(default=None, null=True, verbose_name=_("Current on phase A"))
    current_b = models.FloatField(default=None, null=True, verbose_name=_("Current on phase B"))
    current_c = models.FloatField(default=None, null=True, verbose_name=_("Current on phase C"))
    total_active_power = models.FloatField(default=None, null=True, verbose_name=_("Total active power"))
    total_reactive_power = models.FloatField(default=None, null=True, verbose_name=_("Total reactive power"))
    total_power_factor = models.FloatField(default=None, null=True, verbose_name=_("Total power factor"))

    class Meta:
        verbose_name = _("Real time measurement")

    def __str__(self):
        return f"{self.collection_date} - {self.transductor}"
