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
        read_only_fields = ('active', 'broken')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update()

        return instance


class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()
