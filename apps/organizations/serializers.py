import logging

from rest_framework import serializers

from apps.locations.models import Address, GeographicLocation
from apps.locations.serializers import AddressSerializer, GeographicLocationSerializer
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


# complete this serializer


class EntityListSerializer(serializers.ModelSerializer):
    # hierarchy = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    # parent = serializers.SerializerMethodField()
    entity_type = serializers.CharField(source="get_entity_type_display", read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            # "parent",
            "name",
            "acronym",
            "entity_type",
            # "hierarchy",
            "children",
        ]

    # def get_hierarchy(self, obj):
    #     return obj.get_hierarchy()

    # def get_parent(self, obj):
    #     return obj.parent.name if obj.parent else ""

    def get_children(self, obj):
        return EntityListSerializer(obj.children.all(), many=True).data


class EntityDetailSerializer(serializers.ModelSerializer):
    # address = AddressSerializer(allow_null=True, required=False)
    # geo_location = GeographicLocationSerializer(allow_null=True, required=False)
    # entity_type = serializers.SerializerMethodField()
    # parent = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)

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

    # def get_entity_type(self, obj):
    #     return obj.get_entity_type_display()


class EntityDescendantsSerializer(serializers.ModelSerializer):
    all_descendants = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "acronym",
            "description",
            "entity_type",
            "parent",
            "all_descendants",
        ]

    def get_all_descendants(self, obj):
        return EntityListSerializer(obj.get_all_descendants(), many=True).data
