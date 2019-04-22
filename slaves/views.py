from rest_framework import serializers, viewsets

from .models import Slave
from .serializers import SlaveSerializer

class SlaveViewSet(viewsets.ModelViewSet):
    queryset = Slave.objects.all()
    serializer_class = SlaveSerializer
