from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from .models import Campus
from .serializers import CampusSerializer


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    permission_classes = (permissions.AllowAny,)


# class RealTimeMeasurementViewSet(MeasurementViewSet):
#     serializer_class = RealTimeMeasurementSerializer
#     queryset = RealTimeMeasurement.objects.select_related('transductor').all()
