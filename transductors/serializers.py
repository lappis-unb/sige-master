from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from slaves.models import Slave
from rest_framework.exceptions import NotAcceptable
from rest_framework.exceptions import APIException
from campi.models import Campus

from .models import EnergyTransductor
from .api import create_transductor
from .api import update_transductor

import time
import requests


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'ip_address',
            'port',
            'slave_server',
            'geolocation_latitude',
            'geolocation_longitude',
            'campus',
            'name',
            'broken',
            'active',
            'model',
            'grouping',
            'firmware_version',
            'url'
        )

        read_only_fields = (
            'active',
            'broken'
        )

    def create(self, validated_data):
        existent_group_type = (
            [group.type.name for group in validated_data.get('grouping')]
        )
        valid_groups_type = set(existent_group_type)

        if len(existent_group_type) is not len(valid_groups_type):
            raise NotAcceptable(
                _('You could not link the same transductor for '
                  'two or more groups of the same type.')
            )
        else:
            if(validated_data.get('slave_server') is not None):
                try:
                    slave_server = validated_data.get('slave_server')
                    respose = create_transductor(validated_data, slave_server)
                    if respose.status_code != 201:
                        error_message = _('The collection server %s is unavailable' % slave_server.name)
                        exception = APIException(
                            error_message
                        )
                        exception.status_code = 400
                        raise exception

                except Exception:
                    error_message = _('Could not connect with server %s. try it again latter' % slave_server.name)
                    exception = APIException(
                        error_message
                    )
                    exception.status_code = 400
                    raise exception

            transductor = EnergyTransductor.objects.create(
                serial_number=validated_data.get('serial_number'),
                ip_address=validated_data.get('ip_address'),
                firmware_version=validated_data.get('firmware_version'),
                campus=validated_data.get('campus'),
                name=validated_data.get('name'),
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
            slave_servers = validated_data.get('slave_servers')
            errors = [] 
            for slave_server in slave_servers:
                try:
                    respose = update_transductor(validated_data, slave_server)
                    if respose.status_code != 200:
                        errors.append(
                            _('Could not add transductor to server at ip:') + slave_server.ip_address)
                except requests.exceptions.Timeout:
                    error_messages = _('Could not connect with connect with') + \
                        _('collection server at ip: ') + \
                        slave_server.ip_address
                    errors.append(error_messages)

                if errors.__len__() != 0:
                    exception = APIException(
                        errors
                    )
                    exception.status_code = 400
                    raise exception

            instance.serial_number = validated_data.get('serial_number')
            instance.ip_address = validated_data.get('ip_address')
            instance.firmware_version = validated_data.get('firmware_version')
            instance.campus = validated_data.get('campus')
            instance.name = validated_data.get('name')
            instance.model = validated_data.get('model')
            instance.geolocation_latitude = validated_data.get(
                'geolocation_latitude')
            instance.geolocation_longitude = validated_data.get(
                'geolocation_longitude'
            )

            instance.grouping.set(validated_data.get('grouping'))

            instance.slave_servers.set(validated_data.get('slave_servers'))

            return instance


class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()
