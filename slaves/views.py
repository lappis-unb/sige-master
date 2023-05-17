from rest_framework import permissions, serializers, viewsets
from rest_framework.response import Response

from users.permissions import CurrentADMINUserOnly

from .models import Slave
from .serializers import SlaveSerializer


class SlaveViewSet(viewsets.ModelViewSet):
    queryset = Slave.objects.all()
    serializer_class = SlaveSerializer
    # Para testes de Admin, retirar os permissions.AllowAny
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,) 
