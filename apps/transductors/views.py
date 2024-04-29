import logging

from rest_framework import viewsets

# from apps.organizations.models import Campus
from apps.transductors.models import StatusHistory, Transductor, TransductorModel
from apps.transductors.serializers import (
    TransductorCreateSerializer,
    TransductorDetailSerializer,
    TransductorModelSerializer,
    TransductorStatusDetailSerializer,
    TransductorStatusSerializer,
)


logger = logging.getLogger("apps")


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


class TransductorStatusViewSet(viewsets.ModelViewSet):
    queryset = StatusHistory.objects.all()
    serializer_class = TransductorStatusSerializer
    # permission_classes = [CurrentADMINUserOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrive"]:
            return TransductorStatusDetailSerializer
        return TransductorStatusSerializer
