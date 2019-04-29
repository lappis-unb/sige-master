from rest_framework import serializers, viewsets, mixins

from .models import Measurement, MinutlyMeasurement, QuarterlyMeasurement
from .serializers import MinutlyMeasurementSerializer, QuarterlyMeasurementSerializer


#  this viewset don't inherits from viewsets.ModelViewSet because it 
#  can't have update and create methods so it only inherits from parts of it 
class MinutlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = MinutlyMeasurement.objects.all()
    serializer_class = MinutlyMeasurementSerializer

class QuarterlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = QuarterlyMeasurement.objects.all()
    serializer_class = QuarterlyMeasurementSerializer
