from rest_framework import serializers, viewsets

from django.shortcuts import render

from .models import TransductorModel
from .serializers import TransductorModelSerializer


class TransductorModelViewSet(viewsets.ModelViewSet):
    queryset = TransductorModel.objects.all()
    serializer_class = TransductorModelSerializer
