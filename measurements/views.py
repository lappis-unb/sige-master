from rest_framework import serializers, viewsets, mixins

from transductors.models import EnergyTransductor

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement

from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer
from .serializers import MinutelyActivePowerThreePhase
from .serializers import MinutelyReactivePowerThreePhase
from .serializers import MinutelyApparentPowerThreePhaseSerializer
from .serializers import MinutelyPowerFactorThreePhase
from .serializers import MinutelyDHTVoltageThreePhase
from .serializers import MinutelyDHTCurrentThreePhase
from .serializers import MinutelyTotalActivePower
from .serializers import MinutelyTotalReactivePower
from .serializers import MinutelyTotalApparentPower
from .serializers import MinutelyTotalPowerFactor
from .serializers import VoltageThreePhaseSerializer
from .serializers import FrequencySerializer
from .serializers import CurrentThreePhaseSerializer


#  this viewset don't inherits from viewsets.ModelViewSet because it
#  can't have update and create methods so it only inherits from parts of it
from .models import EnergyTransductor

from .pagination import PostLimitOffsetPagination
from .pagination import PostPageNumberPagination


class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        serial_number = self.request.query_params.get('serial_number', None)

        if serial_number is not None:
            try:
                transductor = EnergyTransductor.objects.get(
                    serial_number=serial_number
                )
            except EnergyTransductor.DoesNotExist:
                return []

        if((start_date is not None) and (end_date is not None)):
            self.queryset = self.queryset.filter(
                collection_date__gte=start_date
            )
            self.queryset = self.queryset.filter(collection_date__lte=end_date)

        return self.queryset.reverse()


class MinutelyMeasurementViewSet(MeasurementViewSet):
    collect = MinutelyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
    serializer_class = MinutelyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    collect = QuarterlyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
    serializer_class = QuarterlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination


class MonthlyMeasurementViewSet(MeasurementViewSet):
    collect = MonthlyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
    serializer_class = MonthlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination

class MinutelyActivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyActivePowerThreePhase


class MinutelyReactivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyReactivePowerThreePhase


class MinutelyApparentPowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    """
    A ViewSet class responsible to get the minutely apparent power
    three phase

    Attributes:

        MinutelyMeasurementViewSet:  a ViewSet class responsible for the
        minutely measurement
    """
    serializer_class = MinutelyApparentPowerThreePhaseSerializer


class MinutelyPowerFactorThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyPowerFactorThreePhase


class MinutelyDHTVoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyDHTVoltageThreePhase


class MinutelyDHTCurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyDHTCurrentThreePhase



class MinutelyTotalActivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyTotalActivePower


class MinutelyTotalReactivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyTotalReactivePower


class MinutelyTotalApparentPowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyTotalApparentPower


class MinutelyTotalPowerFactorViewSet(MinutelyMeasurementViewSet):
    serializer_class = MinutelyTotalPowerFactor


class VoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = VoltageThreePhaseSerializer


class CurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = CurrentThreePhaseSerializer


class FrequencyViewSet(MinutelyMeasurementViewSet):
    serializer_class = FrequencySerializer
