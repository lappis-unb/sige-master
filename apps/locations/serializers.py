import logging

from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.locations.models import Address, City, GeographicLocation, State

logger = logging.getLogger("apps")


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["id", "code", "name", "acronym"]


class CitySerializer(serializers.ModelSerializer):
    state = serializers.SlugRelatedField(slug_field="name", queryset=State.objects.all())

    class Meta:
        model = City
        fields = ("name", "state")


class AddressSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(slug_field="name", queryset=City.objects.all())
    state = serializers.SlugRelatedField(slug_field="name", queryset=State.objects.all(), write_only=True)

    class Meta:
        model = Address
        fields = ["id", "address", "number", "complement", "zip_code", "city", "state"]

    def validate(self, attrs):
        """Verifica se a cidade está no estado correto."""
        # city_data = attrs.get('city')
        # if city_data and city_data['state'].name != 'Estado Esperado':
        #     raise serializers.ValidationError("A cidade deve estar no estado esperado.")
        return attrs

    def create(self, validated_data):
        city_name = validated_data.pop("city")
        state = validated_data.pop("state")

        try:
            with transaction.atomic():
                city, _ = City.objects.get_or_create(name=city_name, state=state)
                address = Address.objects.create(city=city, **validated_data)
        except IntegrityError as e:
            logger.error(f"Error creating address: {e}")
            raise serializers.ValidationError("Error creating address")

        address.city = city
        address.state = state
        return address


class AddressDetailSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name")
    state = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ["id", "address", "number", "complement", "zip_code", "city", "state"]

    def get_state(self, instance):
        return f"{instance.city.state.name} - {instance.city.state.acronym}"


class GeographicLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicLocation
        fields = ["id", "latitude", "longitude", "zoom_level", "tilt", "map_type"]


class BasicGeographicLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicLocation
        fields = ["latitude", "longitude"]
