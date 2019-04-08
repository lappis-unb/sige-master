from rest_framework import viewsets
from .models import Building
from .serializers import BuildingSerializer


class BuildingViewset(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
