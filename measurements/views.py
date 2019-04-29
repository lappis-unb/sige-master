from rest_framework import serializers, viewsets, mixins

from .models import Measurement, MinutlyMeasurement, Qua
from .serializers import MinutlyMeasurementSerializer


#  this viewset don't inherits from viewsets.ModelViewSet because it 
#  can't have update and create methods so it only inherits from parts of it 
class MinutlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = MinutlyMeasurement.objects.all()
    serializer_class = MinutlyMeasurementSerializer

class QuarterlyMeasurement(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = MinutlyMeasurement.objects.all()
    serializer_class = MinutlyMeasurementSerializer
