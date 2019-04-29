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
            'last_data_collection',
            'model',
            'url'
        )
