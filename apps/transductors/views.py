import logging

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.organizations.models import Entity
from apps.transductors.models import StatusHistory, Transductor, TransductorModel
from apps.transductors.serializers import (
    TransductorCreateSerializer,
    TransductorDetailSerializer,
    TransductorModelSerializer,
    TransductorStatusDetailSerializer,
    TransductorStatusSerializer,
)
from apps.utils.helpers import get_boolean

logger = logging.getLogger("apps.transductors.views")


class TransductorModelViewSet(viewsets.ModelViewSet):
    queryset = TransductorModel.objects.all()
    serializer_class = TransductorModelSerializer


class TransductorViewSet(viewsets.ModelViewSet):
    queryset = Transductor.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrive"]:
            return TransductorDetailSerializer
        else:
            return TransductorCreateSerializer

    def list(self, request, *args, **kwargs):
        entity = request.query_params.get("entity", None)
        if not entity:
            return super().list(request, *args, **kwargs)

        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        entity = get_object_or_404(Entity, pk=entity)
        descendants = get_boolean(request.query_params.get("descendants", True))
        if descendants:
            max_depth = request.query_params.get("depth", 0)
            entities = entity.get_descendants(include_self=True, max_depth=int(max_depth))
        else:
            entities = [entity]

        transductors = Transductor.objects.filter(located__in=entities)
        serializer = self.get_serializer(transductors, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)


class TransductorStatusViewSet(viewsets.ModelViewSet):
    queryset = StatusHistory.objects.all()
    serializer_class = TransductorStatusSerializer
    # permission_classes = [CurrentADMINUserOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrive"]:
            return TransductorStatusDetailSerializer
        return TransductorStatusSerializer
