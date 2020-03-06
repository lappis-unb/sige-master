from django.db import models
from django.utils import timezone
from transductors.models import EnergyTransductor
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.utils.translation import gettext_lazy as _


class Tax(models.Model):
    value = models.FloatField(
        default=0,
        verbose_name=_('Tax value')
    )

    registration_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('registration date')
    )


class Measurement(PolymorphicModel):
    collection_date = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name=_('Collection time'),
        help_text=_('This field is required')
    )
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name=_('Energy meter'),
        help_text=_('This field is required')
    )

    def __str__(self):
        return '%s' % self.collection_date

    class Meta:
        abstract = True
        verbose_name = _('Measurement')


class MinutelyMeasurement(Measurement):
    class Meta:
        verbose_name = _('Minutely measurement')

    frequency_a = models.FloatField(
        default=0,
        verbose_name=_('Frequency')
    )

    voltage_a = models.FloatField(
        default=0,
        verbose_name=_('Voltage at phase A')
    )

    voltage_b = models.FloatField(
        default=0,
        verbose_name=_('Voltage at phase B')
    )

    voltage_c = models.FloatField(
        default=0,
        verbose_name=_('Voltage at phase C')
    )

    current_a = models.FloatField(
        default=0,
        verbose_name=_('Current at phase A')
    )

    current_b = models.FloatField(
        default=0,
        verbose_name=_('Current at phase B')
    )

    current_c = models.FloatField(
        default=0,
        verbose_name=_('Current at phase C')
    )

    active_power_a = models.FloatField(
        default=0,
        verbose_name=_('Active power at phase A')
    )

    active_power_b = models.FloatField(
        default=0,
        verbose_name=_('Active power at phase B')
    )

    active_power_c = models.FloatField(
        default=0,
        verbose_name=_('Active power at phase C')
    )

    total_active_power = models.FloatField(
        default=0,
        verbose_name=_('Total active power')
    )

    reactive_power_a = models.FloatField(
        default=0,
        verbose_name=_('Reactive power phase A')
    )

    reactive_power_b = models.FloatField(
        default=0,
        verbose_name=_('Reactive power phase B')
    )

    reactive_power_c = models.FloatField(
        default=0,
        verbose_name=_('Reactive power phase C')
    )

    total_reactive_power = models.FloatField(
        default=0,
        verbose_name=_('Total reactive power')
    )

    apparent_power_a = models.FloatField(
        default=0,
        verbose_name=_('Apparent power on phase A')
    )

    apparent_power_b = models.FloatField(
        default=0,
        verbose_name=_('Apparent power on phase B')
    )

    apparent_power_c = models.FloatField(
        default=0,
        verbose_name=_('Apparent power on phase C')
    )

    total_apparent_power = models.FloatField(
        default=0,
        verbose_name=_('Total apparent power')
    )

    power_factor_a = models.FloatField(
        default=0,
        verbose_name=_('Power factor on phase A')
    )

    power_factor_b = models.FloatField(
        default=0,
        verbose_name=_('Power factor on phase B')
    )

    power_factor_c = models.FloatField(
        default=0,
        verbose_name=_('Power factor on phase C')
    )

    total_power_factor = models.FloatField(
        default=0,
        verbose_name=_('Total power factor')
    )

    dht_voltage_a = models.FloatField(
        default=0,
        verbose_name=_('DHT voltage on phase A')
    )

    dht_voltage_b = models.FloatField(
        default=0,
        verbose_name=_('DHT voltage on phase B')
    )

    dht_voltage_c = models.FloatField(
        default=0,
        verbose_name=_('DHT voltage on phase C')
    )

    dht_current_a = models.FloatField(
        default=0,
        verbose_name=_('DHT current on phase A')
    )

    dht_current_b = models.FloatField(
        default=0,
        verbose_name=_('DHT current on phase B')
    )

    dht_current_c = models.FloatField(
        default=0,
        verbose_name=_('DHT current on phase C')
    )


class QuarterlyMeasurement(Measurement):
    class Meta:
        verbose_name = _('Quartely measurement')

    generated_energy_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Generated energy on peak hours')
    )

    generated_energy_off_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Generated energy not on peak hours')
    )

    consumption_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Consumption on peak hours')
    )

    consumption_off_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Consumption not on peak hours')
    )

    inductive_power_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Inductive power on peak hours')
    )

    inductive_power_off_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Inductive power not on peak hours')
    )

    capacitive_power_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Capacitive power on peak hours')
    )

    capacitive_power_off_peak_time = models.FloatField(
        default=0,
        verbose_name=_('Capacitive power not on peak hours')
    )

    tax = models.ForeignKey(
        Tax,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Tax for peak time collection')
    )


class MonthlyMeasurement(Measurement):
    def __str__(self):
        return '%s' % self.collection_date

    generated_energy_peak_time = models.FloatField(default=0)
    generated_energy_off_peak_time = models.FloatField(default=0)

    consumption_peak_time = models.FloatField(default=0)
    consumption_off_peak_time = models.FloatField(default=0)

    inductive_power_peak_time = models.FloatField(default=0)
    inductive_power_off_peak_time = models.FloatField(default=0)

    capacitive_power_peak_time = models.FloatField(default=0)
    capacitive_power_off_peak_time = models.FloatField(default=0)

    active_max_power_peak_time = models.FloatField(default=0)
    active_max_power_off_peak_time = models.FloatField(default=0)

    reactive_max_power_peak_time = models.FloatField(default=0)
    reactive_max_power_off_peak_time = models.FloatField(
        default=0
    )

    active_max_power_list_peak = ArrayField(
        models.FloatField(), default=None
    )
    active_max_power_list_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    active_max_power_list_off_peak = ArrayField(
        models.FloatField(), default=None
    )

    active_max_power_list_off_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    reactive_max_power_list_peak = ArrayField(
        models.FloatField(), default=None
    )

    reactive_max_power_list_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    reactive_max_power_list_off_peak = ArrayField(
        models.FloatField(), default=None
    )
    reactive_max_power_list_off_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )


class RealTimeMeasurement(Measurement):
    class Meta:
        verbose_name = _('Real time measurement')

    voltage_a = models.FloatField(
        default=0,
        verbose_name=_('Voltage on phase A')
    )

    voltage_b = models.FloatField(
        default=0,
        verbose_name=_('Voltage on phase B')
    )

    voltage_c = models.FloatField(
        default=0,
        verbose_name=_('Voltage on phase C')
    )

    current_a = models.FloatField(
        default=0,
        verbose_name=_('Current on phase A')
    )

    current_b = models.FloatField(
        default=0,
        verbose_name=_('Current on phase B')
    )

    current_c = models.FloatField(
        default=0,
        verbose_name=_('Current on phase C')
    )

    total_active_power = models.FloatField(
        default=0,
        verbose_name=_('Total active power')
    )

    total_reactive_power = models.FloatField(
        default=0,
        verbose_name=_('Total reactive power')
    )

    total_power_factor = models.FloatField(
        default=0,
        verbose_name=_('Total power factor')
    )
