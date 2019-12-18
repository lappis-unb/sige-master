from django.db import models
from transductors.models import EnergyTransductor
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import ArrayField, HStoreField


class Measurement(PolymorphicModel):
    collection_time = models.DateTimeField(blank=False, null=False)
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    def __str__(self):
        return '%s' % self.collection_time

    class Meta:
        abstract = True


class MinutelyMeasurement(Measurement):

    frequency_a = models.FloatField(default=0)

    voltage_a = models.FloatField(default=0)
    voltage_b = models.FloatField(default=0)
    voltage_c = models.FloatField(default=0)

    current_a = models.FloatField(default=0)
    current_b = models.FloatField(default=0)
    current_c = models.FloatField(default=0)

    active_power_a = models.FloatField(default=0)
    active_power_b = models.FloatField(default=0)
    active_power_c = models.FloatField(default=0)
    total_active_power = models.FloatField(default=0)

    reactive_power_a = models.FloatField(default=0)
    reactive_power_b = models.FloatField(default=0)
    reactive_power_c = models.FloatField(default=0)
    total_reactive_power = models.FloatField(default=0)

    apparent_power_a = models.FloatField(default=0)
    apparent_power_b = models.FloatField(default=0)
    apparent_power_c = models.FloatField(default=0)
    total_apparent_power = models.FloatField(default=0)

    power_factor_a = models.FloatField(default=0)
    power_factor_b = models.FloatField(default=0)
    power_factor_c = models.FloatField(default=0)
    total_power_factor = models.FloatField(default=0)

    dht_voltage_a = models.FloatField(default=0)
    dht_voltage_b = models.FloatField(default=0)
    dht_voltage_c = models.FloatField(default=0)

    dht_current_a = models.FloatField(default=0)
    dht_current_b = models.FloatField(default=0)
    dht_current_c = models.FloatField(default=0)


class QuarterlyMeasurement(Measurement):

    generated_energy_peak_time = models.FloatField(default=0)
    generated_energy_off_peak_time = models.FloatField(default=0)
    consumption_peak_time = models.FloatField(default=0)
    consumption_off_peak_time = models.FloatField(default=0)
    inductive_power_peak_time = models.FloatField(default=0)
    inductive_power_off_peak_time = models.FloatField(default=0)
    capacitive_power_peak_time = models.FloatField(default=0)
    capacitive_power_off_peak_time = models.FloatField(default=0)


class MonthlyMeasurement(Measurement):

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

    # When using HStoreField remember to install the extension in the migration
    active_max_power_list_peak_time = ArrayField(
        HStoreField(), default=None
    )
    active_max_power_list_off_peak_time = ArrayField(
        HStoreField(), default=None
    )
    reactive_max_power_list_peak_time = ArrayField(
        HStoreField(), default=None
    )
    reactive_max_power_list_off_peak_time = ArrayField(
        HStoreField(), default=None
    )


class RealTimeMeasurement(Measurement):
    voltage_a = models.FloatField(default=0)
    voltage_b = models.FloatField(default=0)
    voltage_c = models.FloatField(default=0)

    current_a = models.FloatField(default=0)
    current_b = models.FloatField(default=0)
    current_c = models.FloatField(default=0)

    total_active_power = models.FloatField(default=0)
    total_reactive_power = models.FloatField(default=0)
    total_power_factor = models.FloatField(default=0)
