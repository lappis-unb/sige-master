from rest_framework import serializers

from .models import EnergyTransductor


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'ip_address',
            'location',
            'latitude',
            'longitude',
            'name',
            'broken',
            'active',
            'creation_date',
            'calibration_date',
            'measurements_minutelymeasurement',
            'measurements_quarterlymeasurement',
            'measurements_monthlymeasurement',
            'last_data_collection',
            'model',
            'url'
        )
        read_only_fields = ('active', 'broken')

class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()
