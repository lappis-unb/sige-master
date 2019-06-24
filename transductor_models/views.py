from rest_framework import serializers, viewsets, permissions

from django.shortcuts import render

from .models import TransductorModel
from .serializers import TransductorModelSerializer


class TransductorModelViewSet(viewsets.ModelViewSet):
    queryset = TransductorModel.objects.all()
    serializer_class = TransductorModelSerializer
    permission_classes = (permissions.IsAdminUser,)
