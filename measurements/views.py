from rest_framework import serializers, viewsets, mixins

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer


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


class MonthlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = MonthlyMeasurement.objects.all()
    serializer_class = MonthlyMeasurementSerializer
