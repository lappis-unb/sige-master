from rest_framework import serializers
from slaves.models import Slave

from .models import EnergyTransductor


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'ip_address',
            'geolocation_latitude',
            'geolocation_longitude',
            'name',
            'broken',
            'active',
            'creation_date',
            'model',
            'url'
        )
        read_only_fields = (
            'creation_date',
            'serial_number',
            'active',
            'broken'
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update()

        return instance


class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()
