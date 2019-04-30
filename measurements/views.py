from rest_framework import serializers, viewsets, mixins

from .models import Measurement, MinutelyMeasurement, QuarterlyMeasurement
from .serializers import MinutelyMeasurementSerializer, QuarterlyMeasurementSerializer


#  this viewset don't inherits from viewsets.ModelViewSet because it 
#  can't have update and create methods so it only inherits from parts of it 
class MinutelyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = MinutelyMeasurement.objects.all()
    serializer_class = MinutelyMeasurementSerializer

class QuarterlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = QuarterlyMeasurement.objects.all()
    serializer_class = QuarterlyMeasurementSerializer
