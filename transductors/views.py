from django.shortcuts import render

from rest_framework import serializers, viewsets, permissions

from .models import EnergyTransductor
from .serializers import EnergyTransductorSerializer


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = EnergyTransductorSerializer
    permission_classes = (permissions.AllowAny,)
