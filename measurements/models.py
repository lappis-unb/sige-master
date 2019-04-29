from django.db import models


class Measurement(models.Model):
    #TODO add transductor
    collection_time = models.DateTimeField(blank=False,null=False)

    class Meta:
        abstract = True

class MinutlyMeasurement(Measurement):

    def __str__(self):
        return '%s' % self.collection_date

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