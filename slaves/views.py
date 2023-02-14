from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions
from rest_framework.response import Response

from .models import Slave
from .serializers import SlaveSerializer

from users.permissions import CurrentADMINUserOnly


class SlaveViewSet(viewsets.ModelViewSet):
    queryset = Slave.objects.all()
    serializer_class = SlaveSerializer
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,) # Para testes de Admin, retirar os permissions.AllowAny
