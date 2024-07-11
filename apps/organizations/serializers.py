import logging

from rest_framework import serializers

from apps.locations.serializers import (
    AddressDetailSerializer,
    BasicGeographicLocationSerializer,
)
from apps.organizations.models import Entity, Organization

logger = logging.getLogger("apps")


class EntityCreateSerializer(serializers.ModelSerializer):
    children = serializers.ListField(write_only=True, child=serializers.JSONField(), required=False)

    class Meta:
        model = Entity
        fields = [
            "name",
            "acronym",
            "entity_type",
            "parent",
            "description",
            "children",
        ]

    def create(self, validated_data):
        children_data = validated_data.pop("children", [])
        entity = Entity.objects.create(**validated_data)
        for child_data in children_data:
            child_data["parent"] = entity
            self.create(child_data)
        return entity


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "name",
            "acronym",
            "entity_type",
            "description",
            "cnpj",
            "website",
            "email",
            "phone",
        ]

    def create(self, validated_data):
        children_data = validated_data.pop("children", [])
        organization = Organization.objects.create(**validated_data)
        for child_data in children_data:
            child_data["parent"] = organization
            self.create(child_data)
        return organization


class EntityTreeListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    entity_type = serializers.CharField(source="get_entity_type_display", read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "entity_type",
            "name",
            "acronym",
            "parent",
            "children",
        ]

    def get_children(self, obj):
        return EntityTreeListSerializer(obj.children.all(), many=True).data


class EntityDetailSerializer(serializers.ModelSerializer):
    address = AddressDetailSerializer()
    geo_location = BasicGeographicLocationSerializer()
    entity_type = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "acronym",
            "description",
            "entity_type",
            "address",
            "geo_location",
            "parent",
        ]

    def get_parent(self, obj):
        return f"{obj.parent.acronym} - {obj.parent.name}" if obj.parent else ""

    def get_entity_type(self, obj):
        return obj.get_entity_type_display()
