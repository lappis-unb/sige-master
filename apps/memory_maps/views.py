from rest_framework.viewsets import ModelViewSet

from apps.memory_maps.models import MemoryMap
from apps.memory_maps.serializers import MemoryMapSerializer


class MemoryMapViewSet(ModelViewSet):
    queryset = MemoryMap.objects.all()
    serializer_class = MemoryMapSerializer
