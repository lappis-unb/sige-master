from rest_framework import serializers

from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import EnergyTransductor
from .models import Tax

from django.db.models import Sum


class MinutelyMeasurementSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MinutelyMeasurement
        fields = ('id',
                  'transductor',
                  'collection_date',
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
                  'collection_date',
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


class ThreePhaseSerializer(MinutelyMeasurementSerializer):
    """
    Class responsible to define a serializer which convert apparent
    three phase transductor fields data to JSON

    Attributes:

        model (MinutelyMeasurement): The model which defines the type of
        measurement.
        fields (tuple): Generic representation of all threephasic measurements.
            .. note::
                The tuple elements must be of str type.

    Example of use:

    >>> queryset = MinutelyMeasurement.objects.all()
        serializer_class = MinutelyApparentPowerThreePhase
    """
    phase_a = serializers.ListField(default=[])
    phase_b = serializers.ListField(default=[])
    phase_c = serializers.ListField(default=[])

    class Meta:
        model = MinutelyMeasurement
        fields = (
            'id',
            'transductor',
            'phase_a',
            'phase_b',
            'phase_c'
        )


class MeasurementSerializer(MinutelyMeasurementSerializer):
    measurements = serializers.ListField(default=[])

    class Meta:
        model = MinutelyMeasurement
        fields = (
            'id',
            'transductor',
            'measurements'
        )


class QuarterlySerializer(QuarterlyMeasurementSerializer):
    measurements = serializers.ListField(default=[])

    class Meta:
        model = QuarterlyMeasurement
        fields = (
            'id',
            'measurements'
        )


class RealTimeMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    consumption = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MinutelyMeasurement
        fields = ('id',
                  'transductor_id',
                  'collection_date',
                  'voltage_a',
                  'voltage_b',
                  'voltage_c',
                  'current_a',
                  'current_b',
                  'current_c',
                  'total_active_power',
                  'total_reactive_power',
                  'total_power_factor',
                  'consumption',
                  'url')

    def get_consumption(self, obj):
        consumptions = ['consumption_peak_time', 'consumption_off_peak_time']
        info = QuarterlyMeasurement.objects.filter(
            transductor=EnergyTransductor.objects.get(
                pk=self.__dict__['_args'][0].last().transductor_id
            )
        ).aggregate(
            total_consumption=(Sum(consumptions[0]) + Sum(consumptions[1]))
        )

        return info['total_consumption']


class TaxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tax
        fields = (
            'id',
            'calue_peak',
            'value_off_peak',
            'url'
        )
