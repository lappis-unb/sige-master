from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from .models import Campus, Tariff
from .serializers import CampusSerializer, TariffSerializer


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    permission_classes = (permissions.AllowAny,)

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = (permissions.AllowAny,)
