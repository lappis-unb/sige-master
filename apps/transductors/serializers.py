import logging

from django.core.validators import MaxValueValidator
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.locations.models import GeographicLocation
from apps.locations.serializers import BasicGeographicLocationSerializer
from apps.memory_maps.models import MemoryMap
from apps.transductors.models import (
    Status,
    StatusHistory,
    Transductor,
    TransductorModel,
)
from apps.transductors.utils import parse_uploaded_csv_file
from apps.transductors.validators import CsvFileValidator

logger = logging.getLogger("apps")


class TransductorModelSerializer(serializers.ModelSerializer):
    memory_map_file = serializers.FileField(validators=[CsvFileValidator()])
    max_block_size = serializers.IntegerField(validators=[MaxValueValidator(125)])

    class Meta:
        model = TransductorModel
        fields = [
            "id",
            "manufacturer",
            "name",
            "protocol",
            "read_function",
            "modbus_addr_id",
            "max_block_size",
            "base_address",
            "notes",
            "memory_map_file",
        ]

    def validate_max_block_size(self, value):
        if value > 125:
            raise serializers.ValidationError(
                "The maximum number of contiguous registers that can be read using pymodbus is 125"
            )
        return value

    def create(self, validated_data):
        """
        Responsibility to create the instance of TransductorModel and creating related objects (MemoryMap)
        based on data passed in through the validated_data object (csv_map).
        """

        try:
            with transaction.atomic():
                csv_data = parse_uploaded_csv_file(validated_data["memory_map_file"])
                transductor_model = super().create(validated_data)

                MemoryMap.create_from_csv(
                    transductor_model,
                    csv_data,
                    validated_data["max_block_size"],
                )
                return transductor_model
        except (IntegrityError, ValidationError) as e:
            raise ValidationError(f"An exception of type {type(e).__name__} occurred: {e}")

    def update(self, instance, validated_data):
        csv_data = parse_uploaded_csv_file(validated_data["memory_map_file"])

        try:
            instance.memory_map.update_from_csv(
                csv_data,
                validated_data["max_length"],
            )
        except Exception as e:
            raise ValidationError(f"An exception of type {type(e).__name__} occurred: {e}")
        return super().update(instance, validated_data)


class TransductorCreateSerializer(serializers.ModelSerializer):
    port = serializers.IntegerField(validators=[MaxValueValidator(65535)])
    status = serializers.ChoiceField(choices=Status.choices, write_only=True, required=True)
    geo_location = BasicGeographicLocationSerializer()

    class Meta:
        model = Transductor
        fields = [
            "id",
            "model",
            "is_generator",
            "located",
            "serial_number",
            "ip_address",
            "port",
            "firmware_version",
            "status",
            "installation_date",
            "geo_location",
        ]

    def create(self, validated_data):
        initial_status = validated_data.pop("status")
        notes = f"Transductor created with status: {Status(initial_status).label}"
        geo_location_data = validated_data.pop("geo_location")

        try:
            with transaction.atomic():
                geo_location = GeographicLocation.objects.create(**geo_location_data)
                transductor = Transductor.objects.create(geo_location=geo_location, **validated_data)

                StatusHistory.objects.create(
                    transductor=transductor,
                    status=initial_status,
                    notes=notes,
                )
            return transductor
        except IntegrityError as e:
            raise ValidationError(f"An exception of type {type(e).__name__} occurred: {e}")


class TransductorDetailSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="model.name")
    located = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    uptime = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Transductor
        fields = [
            "id",
            "model",
            "serial_number",
            "ip_address",
            "port",
            "located",
            "installation_date",
            "firmware_version",
            "status",
            "uptime",
            "description",
        ]

    def get_status(self, instance):
        return instance.current_status.get_status_display()

    def get_located(self, instance):
        return f"{instance.located.acronym} {instance.located.name}"


class TransductorStatusDetailSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    transductor = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()

    class Meta:
        model = StatusHistory
        fields = [
            "id",
            "transductor",
            "model",
            "status",
            "start_time",
            "end_time",
            # "duration",
            "notes",
        ]

    def get_transductor(self, instance):
        return instance.transductor.ip_address

    def get_status(self, instance):
        return instance.get_status_display()

    def get_model(self, instance):
        return f"{instance.transductor.model.manufacturer} {instance.transductor.model.name}"


class TransductorStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Status.choices, write_only=True, required=True)
    notes = serializers.CharField(required=False)

    class Meta:
        model = StatusHistory
        fields = [
            "id",
            "transductor",
            "start_time",
            "status",
            "notes",
        ]
