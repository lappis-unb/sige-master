import logging

from rest_framework import viewsets
from rest_framework.response import Response

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
        entity_id = request.query_params.get("entity", None)
        if not entity_id:
            return super().list(request, *args, **kwargs)

        inc_desc = get_boolean(request.query_params.get("inc_desc", "true"))
        transductors = self.get_queryset().entity(entity_id, inc_desc)
        serializer = self.get_serializer(transductors, many=True)
        return Response(serializer.data)


class TransductorStatusViewSet(viewsets.ModelViewSet):
    queryset = StatusHistory.objects.all()
    serializer_class = TransductorStatusSerializer
    # permission_classes = [CurrentADMINUserOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrive"]:
            return TransductorStatusDetailSerializer
        return TransductorStatusSerializer
