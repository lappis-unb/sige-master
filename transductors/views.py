import json

from django.shortcuts import render

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions, status

from .api import *
from slaves.models import Slave
from .models import EnergyTransductor
from .serializers import EnergyTransductorSerializer, AddToServerSerializer
from django.http import Http404


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = EnergyTransductorSerializer
    permission_classes = (permissions.AllowAny,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            response = delete_transductor(instance, instance.slave_server)
            if response.status_code is not 204:
               return Response(status=status.HTTP_400_BAD_REQUEST) 
            instance.delete()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_to_server(self, request, pk=None):
        serializer_class = AddToServerSerializer(data=request.data)
        if serializer_class.is_valid():
            slave_server = Slave.objects.get(
                id=serializer_class.data["slave_id"]
            )
            response = slave_server.add_transductor(self.get_object())
            return Response(data=json.loads(response.content),
                            status=response.status_code)
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
