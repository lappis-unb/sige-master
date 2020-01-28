from rest_framework import serializers
from slaves.models import Slave
from rest_framework.exceptions import NotAcceptable
from .models import EnergyTransductor


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'ip_address',
            'physical_location',
            'geolocation_latitude',
            'geolocation_longitude',
            'firmware_version',
            'campus',
            'name',
            'broken',
            'active',
            'creation_date',
            'calibration_date',
            'model',
            'grouping',
            'url'
        )
        read_only_fields = ('active', 'broken')

    def create(self, validated_data):
        existent_group_type = (
            [group.type.name for group in validated_data.get('grouping')]
        )
        valid_groups_type = set(existent_group_type)

        if len(existent_group_type) is not len(valid_groups_type):
            raise NotAcceptable(
                'You could not link the same transductor for '
                'two or more groups of the same type.'
            )
        else:
            transductor = EnergyTransductor.objects.create(
                serial_number=validated_data.get('serial_number'),
                ip_address=validated_data.get('ip_address'),
                physical_location=validated_data.get('physical_location'),
                firmware_version=validated_data.get('firmware_version'),
                campus=validated_data.get('campus'),
                name=validated_data.get('name'),
                creation_date=validated_data.get('creation_date'),
                calibration_date=validated_data.get('calibration_date'),
                model=validated_data.get('model'),
                geolocation_latitude=validated_data.get('geolocation_latitude'),
                geolocation_longitude=validated_data.get(
                    'geolocation_longitude'
                )
            )

            for group in validated_data.get('grouping'):
                transductor.grouping.add(group)

            return transductor

    def update(self, instance, validated_data):
        existent_group_type = (
            [
                group.type.name for group in set(validated_data.get('grouping'))
            ]
        )
        valid_groups_type = set(existent_group_type)

        if len(existent_group_type) is not len(valid_groups_type):
            raise NotAcceptable(
                'You could not link the same transductor for '
                'two or more groups of the same type.'
            )
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.update()

            return instance


class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()
