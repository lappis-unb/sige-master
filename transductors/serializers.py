import logging

from django.core.validators import MaxValueValidator
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.status import is_client_error, is_server_error, is_success

from transductors.api import create_transductor, delete_transductor, update_transductor
from transductors.models import EnergyTransductor
from transductors.validators import latitude_validator, longitude_validator

logger = logging.getLogger(__name__)


class EnergyTransductorSerializer(serializers.ModelSerializer):
    geolocation_latitude = serializers.FloatField(validators=[latitude_validator])
    geolocation_longitude = serializers.FloatField(validators=[longitude_validator])
    power = serializers.IntegerField()
    port = serializers.IntegerField(validators=[MaxValueValidator(65535)])

    class Meta:
        model = EnergyTransductor
        fields = (
            "id",
            "model",
            "serial_number",
            "ip_address",
            "port",
            "firmware_version",
            "campus",
            "geolocation_latitude",
            "geolocation_longitude",
            "power",
            "is_generator",
            "broken",
            "active",
            "name",
            "slave_server",
            "grouping",
            "history",
        )

        read_only_fields = ("active", "broken")

    def validate_grouping_data(self, grouping_data):
        existent_group_type = [group.type.name for group in grouping_data]
        valid_groups_type = set(existent_group_type)

        if len(existent_group_type) != len(valid_groups_type):
            error_message = _("You could not link the same transductor for " "two or more groups of the same type.")
            raise serializers.ValidationError(error_message)

    def create(self, validated_data):
        grouping_data = validated_data.pop("grouping", [])
        self.validate_grouping_data(grouping_data)

        transductor = EnergyTransductor.objects.create(**validated_data)
        if transductor.slave_server:
            sync_slave, response = self.handle_slave_transductor(transductor, create_transductor)

            if not sync_slave:
                transductor.delete()
                raise serializers.ValidationError(detail=response.text, code=response.status_code)

        transductor.grouping.set(grouping_data)
        return transductor

    def delete(self, instance):
        if instance.slave_server is None:
            return instance.delete()

        sync_slave, response = self.handle_slave_transductor(instance, delete_transductor)

        if not sync_slave:
            raise serializers.ValidationError(f"Failed to delete in slave API. Status code: {response.status_code}")
        return instance.delete()

    def handle_slave_transductor(self, instance, action_func):
        try:
            response = action_func(instance)
            if is_success(response.status_code):
                return (True, response.json)

            elif is_client_error(response.status_code):
                if isinstance(response, dict):
                    response = format_serializer_errors(response)
                return (False, response)

            elif is_server_error(response.status_code):
                instance.pending_sync = True
                return (True, response)

            else:
                raise serializers.ValidationError(detail="Unknown error occurred")

        except Exception as e:
            logger.exception(f"Exception when updating slave transductor: {e}")
            raise serializers.ValidationError(e)

    def update(self, instance, validated_data):
        if instance.campus != validated_data["campus"]:
            error_message = _("Cannot update campus field.")
            raise serializers.ValidationError(error_message)

        grouping_data = validated_data.pop("grouping", [])
        self.validate_grouping_data(grouping_data)

        new_slave = validated_data.pop("slave_server", None)
        old_slave = instance.slave_server

        for key, value in validated_data.items():
            setattr(instance, key, value)

        response = self.handle_atomic_change_slave(instance, old_slave, new_slave)
        logger.info("response: %s", response)

        instance.save()
        instance.grouping.set(grouping_data)
        return instance

    @transaction.atomic
    def handle_atomic_change_slave(self, instance, old_slave, new_slave):
        if old_slave != new_slave:
            if new_slave:
                instance.slave_server = new_slave
                sync_slave, response = self.handle_slave_transductor(instance, create_transductor)
                if not sync_slave:
                    logger.error(
                        "Failed to delete in old slave API. Status code: %s",
                        response.status_code,
                    )
                    raise serializers.ValidationError(
                        f"Failed to create in new slave API. Status code: {response.status_code}"
                    )
            if old_slave:
                sync_slave, response = self.handle_slave_transductor(instance, delete_transductor)
                if not sync_slave:
                    logger.error(
                        "Failed to delete in old slave API. Status code: %s",
                        response.status_code,
                    )
                    raise serializers.ValidationError(
                        f"Failed to delete in old slave API. Status code: {response.status_code}"
                    )
        else:
            instance.slave_server = new_slave
            sync_slave, response = self.handle_slave_transductor(instance, update_transductor)
            if not sync_slave:
                logger.error(
                    "Failed to delete in old slave API. Status code: %s",
                    response.status_code,
                )
                raise serializers.ValidationError(
                    f"Failed to update in new slave API. Status code: {response.status_code}"
                )
        return response


class AddToServerSerializer(serializers.Serializer):
    slave_id = serializers.IntegerField()


class EnergyTransductorListSerializer(serializers.ModelSerializer):
    current_precarious_events_count = serializers.IntegerField()
    current_critical_events_count = serializers.IntegerField()
    events_last72h = serializers.IntegerField()
    campus = serializers.CharField()
    grouping = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = EnergyTransductor
        fields = (
            "id",
            "serial_number",
            "campus",
            "name",
            "active",
            "broken",
            "model",
            "grouping",
            "current_precarious_events_count",
            "current_critical_events_count",
            "events_last72h",
        )


def format_serializer_errors(serializer):
    errors = serializer.errors
    formatted_errors = {}

    for field, error_messages in errors.items():
        formatted_error_messages = [str(error_message) for error_message in error_messages]
        formatted_errors[field] = formatted_error_messages

    return formatted_errors
