from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from slaves.models import Slave
from rest_framework.exceptions import NotAcceptable
from rest_framework.exceptions import APIException
from campi.models import Campus
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import EnergyTransductor
from .api import check_connection
from .api import create_transductor
from .api import update_transductor
from .api import delete_transductor

import time
import requests


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'id',
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
            id_in_slave = 0
            if(validated_data.get('slave_server') is not None):
                try:
                    slave_server = validated_data.get('slave_server')
                    response = create_transductor(validated_data, slave_server)
                    if response.status_code != 201:
                        error_message = _(
                            'The collection server %s is unavailable' 
                            % slave_server.name)
                        exception = APIException(
                            error_message
                        )
                        exception.status_code = 400
                        raise exception
                    r = response.json()
                    id_in_slave = r['id']
                except Exception:
                    error_message = _(
                        'Could not connect with server %s. try it again latter'
                        % slave_server.name)
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
                ),
                slave_server=slave_server,
                id_in_slave=id_in_slave
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
                _('You could not link the same transductor for '
                  'two or more groups of the same type.')
            )
        old_slave_server = instance.slave_server
        new_slave_server = validated_data.get('slave_server')

        errors = []
        if new_slave_server != old_slave_server:
            if not check_connection(old_slave_server):
                error_message = _(
                    'Could not disconnect from server %s. try it again latter'
                    % old_slave_server.name)
                errors.append(error_message)

            if not check_connection(new_slave_server):
                error_message = _(
                    'Could not connect wit h server %s. try it again latter' 
                    % new_slave_server.name)

                errors.append(error_message)

            if errors.__len__() > 0:
                exception = APIException(
                    errors
                )
                exception.status_code = 400
                raise exception

            else:
                try:
                    if old_slave_server is not None:
                        delete_transductor(
                            instance.id_in_slave, instance, old_slave_server)

                except Exception:
                    error_messages = _(
                        'Could not disconnect from server %s.' 
                        'try it again latter'
                        % old_slave_server.name)

                    errors.append(error_messages)
                try:
                    if new_slave_server is not None:
                        response = create_transductor(
                            validated_data, new_slave_server)
                except Exception:
                    error_message = _(
                        'Could not connect with server %s. try it again latter'
                        % new_slave_server.name)

                    errors.append(error_messages)
                r = response.json()
                instance.id_in_slave = r['id']

        else:
            try:
                if old_slave_server is not None:
                    update_transductor(
                        instance.id, validated_data, old_slave_server)
            except Exception:
                error_message = _(
                    'Could not connect with server %s. try it again latter'
                    % new_slave_server.name)

                errors.append(error_messages)

        if errors.__len__() > 0:
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

        instance.slave_server = new_slave_server

        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            slave_server = instance.slave_server
            if slave_server is not None:
                delete_transductor(instance.id_in_slave, instance, slave_server)            
            instance.delete()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()
