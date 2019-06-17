from rest_framework import viewsets
from rest_framework import permissions

from .models import Building
from .serializers import BuildingSerializer


class BuildingViewset(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
