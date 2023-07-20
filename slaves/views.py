from rest_framework import permissions, viewsets

from slaves.models import Slave
from slaves.serializers import SlaveSerializer
from users.permissions import CurrentADMINUserOnly


class SlaveViewSet(viewsets.ModelViewSet):
    queryset = Slave.objects.all()
    serializer_class = SlaveSerializer
    # Para testes de Admin, retirar os permissions.AllowAny
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,)
