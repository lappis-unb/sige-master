from rest_framework import serializers, viewsets

from .models import Campus
from .serializers import CampusSerializer


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
