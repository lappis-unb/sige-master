from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import permissions

from .models import Campus, Tariff
from .serializers import CampusSerializer, TariffSerializer
from users.permissions import CurrentADMINUserOnly


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,) # Para testes de Admin, retirar os permissions.AllowAny


class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,) # Para testes de Admin, retirar os permissions.AllowAny


    def get_queryset(self):
        campus = get_object_or_404(
            Campus,
            pk=self.kwargs['campi_pk']
        )
        return Tariff.objects.filter(campus=campus)
