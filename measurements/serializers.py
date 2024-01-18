from rest_framework import serializers

from measurements.models import (
    EnergyTransductor,
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    Tax,
)


class MinutelyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor",
            "frequency_a",
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "active_power_a",
            "active_power_b",
            "active_power_c",
            "total_active_power",
            "reactive_power_a",
            "reactive_power_b",
            "reactive_power_c",
            "total_reactive_power",
            "apparent_power_a",
            "apparent_power_b",
            "apparent_power_c",
            "total_apparent_power",
            "power_factor_a",
            "power_factor_b",
            "power_factor_c",
            "total_power_factor",
            "dht_voltage_a",
            "dht_voltage_b",
            "dht_voltage_c",
            "dht_current_a",
            "dht_current_b",
            "dht_current_c",
            "collection_date",
        )


class QuarterlyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuarterlyMeasurement
        fields = (
            "id",
            "transductor",
            "is_calculated",
            "generated_energy_peak_time",
            "generated_energy_off_peak_time",
            "consumption_peak_time",
            "consumption_off_peak_time",
            "inductive_power_peak_time",
            "inductive_power_off_peak_time",
            "capacitive_power_peak_time",
            "capacitive_power_off_peak_time",
            "collection_date",
        )


class MonthlyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyMeasurement
        fields = (
            "id",
            "transductor",
            "generated_energy_peak_time",
            "generated_energy_off_peak_time",
            "consumption_peak_time",
            "consumption_off_peak_time",
            "inductive_power_peak_time",
            "inductive_power_off_peak_time",
            "capacitive_power_peak_time",
            "capacitive_power_off_peak_time",
            "active_max_power_peak_time",
            "active_max_power_off_peak_time",
            "reactive_max_power_peak_time",
            "reactive_max_power_off_peak_time",
            "collection_date"
        )


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

    max = serializers.FloatField(default=0)
    min = serializers.FloatField(default=0)
    phase_a = serializers.ListField(default=[])
    phase_b = serializers.ListField(default=[])
    phase_c = serializers.ListField(default=[])

    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor",
            "max",
            "min",
            "phase_a",
            "phase_b",
            "phase_c",
        )


class MeasurementSerializer(MinutelyMeasurementSerializer):
    max = serializers.FloatField(default=0)
    min = serializers.FloatField(default=0)
    measurements = serializers.ListField(default=[])

    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor",
            "max",
            "min",
            "measurements",
        )


class QuarterlySerializer(QuarterlyMeasurementSerializer):
    measurements = serializers.ListField(default=[])

    class Meta:
        model = QuarterlyMeasurement
        fields = ("id", "measurements")


class RealTimeMeasurementSerializer(serializers.ModelSerializer):
    consumption = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor_id",
            "collection_date",
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "total_active_power",
            "total_reactive_power",
            "total_power_factor",
            "consumption",
        )

    def get_consumption(self, obj):
        transductor_id = obj.transductor_id
        transductor = EnergyTransductor.objects.get(id=transductor_id)

        last_measurement = transductor.measurements_quarterlymeasurement.order_by("-collection_date").last()

        if last_measurement is not None:
            return (
                last_measurement.consumption_peak_time
                if last_measurement.consumption_peak_time is not None
                else last_measurement.consumption_off_peak_time
            )

        return None


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = (
            "id",
            "value_peak",
            "value_off_peak",
        )
