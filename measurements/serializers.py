from rest_framework import serializers

from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField


class MinutelyMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = ('id',
                  'transductor',
                  'collection_time',
                  'frequency_a',
                  'voltage_a',
                  'voltage_b',
                  'voltage_c',
                  'current_a',
                  'current_b',
                  'current_c',
                  'active_power_a',
                  'active_power_b',
                  'active_power_c',
                  'total_active_power',
                  'reactive_power_a',
                  'reactive_power_b',
                  'reactive_power_c',
                  'total_reactive_power',
                  'apparent_power_a',
                  'apparent_power_b',
                  'apparent_power_c',
                  'total_apparent_power',
                  'power_factor_a',
                  'power_factor_b',
                  'power_factor_c',
                  'total_power_factor',
                  'dht_voltage_a',
                  'dht_voltage_b',
                  'dht_voltage_c',
                  'dht_current_a',
                  'dht_current_b',
                  'dht_current_c',
                  'transductor',
                  'url')


class QuarterlyMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuarterlyMeasurement
        fields = ('id',
                  'collection_time',
                  'generated_energy_peak_time',
                  'generated_energy_off_peak_time',
                  'consumption_peak_time',
                  'consumption_off_peak_time',
                  'inductive_power_peak_time',
                  'inductive_power_off_peak_time',
                  'capacitive_power_peak_time',
                  'capacitive_power_off_peak_time',
                  'transductor',
                  'url')


class MonthlyMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonthlyMeasurement
        fields = ('id',
                  'generated_energy_peak_time',
                  'generated_energy_off_peak_time',
                  'consumption_peak_time',
                  'consumption_off_peak_time',
                  'inductive_power_peak_time',
                  'inductive_power_off_peak_time',
                  'capacitive_power_peak_time',
                  'capacitive_power_off_peak_time',
                  'active_max_power_peak_time',
                  'active_max_power_off_peak_time',
                  'reactive_max_power_peak_time',
                  'reactive_max_power_off_peak_time',
                  'active_max_power_list_peak_time',
                  'active_max_power_list_off_peak_time',
                  'reactive_max_power_list_peak_time',
                  'reactive_max_power_list_off_peak_time',
                  'url')


class VoltageThreePhaseSerializer(MinutelyMeasurementSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = (
            'id',
            'transductor',
            'collection_time',
            'voltage_a',
            'voltage_b',
            'voltage_c'
        )


class CurrentThreePhaseSerializer(MinutelyMeasurementSerializer):
    list_current_a = serializers.ListField(default=[])
    list_current_b = serializers.ListField(default=[])
    list_current_c = serializers.ListField(default=[])

    class Meta:
        model = MinutelyMeasurement
        fields = (
            'id',
            'transductor',
            'collection_time',
            'list_current_a',
            'list_current_b',
            'list_current_c'
        )

    def create(self, validated_data):
        validated_data.list_current_a = [1]
        validated_data.list_current_b = [2]
        validated_data.list_current_c = [3]
        return super().create(validated_data)

class FrequencySerializer(MinutelyMeasurementSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = (
            'id',
            'transductor',
            'collection_time',
            'frequency_a'
        )
