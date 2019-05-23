from django.shortcuts import render

from rest_framework import serializers, viewsets

from .models import EnergyTransductor
from .serializers import EnergyTransductorSerializer


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = EnergyTransductorSerializer
