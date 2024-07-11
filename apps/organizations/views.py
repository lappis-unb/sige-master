from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.organizations.models import Entity, Organization
from apps.organizations.serializers import (
    EntityCreateSerializer,
    EntityDetailSerializer,
    EntityTreeListSerializer,
    OrganizationCreateSerializer,
)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(parent__isnull=True)
        return self.queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["create", "update", "partial_update"]:
            return EntityCreateSerializer
        if self.action == "list":
            return EntityTreeListSerializer
        else:
            return EntityDetailSerializer

    @action(detail=True, methods=["get"])
    def descendants(self, request, pk=None):
        root_entity = self.get_object()
        serializer = EntityTreeListSerializer(root_entity)
        return Response(serializer.data)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationCreateSerializer
