from rest_framework import viewsets

from apps.organizations.models import Entity, Organization
from apps.organizations.serializers import (
    EntityCreateSerializer,
    EntityDetailSerializer,
    EntityListSerializer,
    OrganizationCreateSerializer,
)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntityListSerializer

    def get_queryset(self):
        return Entity.objects.filter(parent=None)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return EntityCreateSerializer
        if self.action == "list":
            return EntityListSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return EntityDetailSerializer
        else:
            return EntityListSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationCreateSerializer
