import logging

from django_filters import rest_framework as filters

from .models import CumulativeMeasurement, InstantMeasurement

logger = logging.getLogger("apps.measurements.filters")


class BaseMeasurementFilter(filters.FilterSet):
    transductor = filters.NumberFilter(field_name="transductor")
    start_date = filters.DateTimeFilter(field_name="collection_date", lookup_expr="gte")
    end_date = filters.DateTimeFilter(field_name="collection_date", lookup_expr="lte")


class InstantMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = InstantMeasurement
        fields = ["transductor", "start_date", "end_date"]


class CumulativeMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = CumulativeMeasurement
        fields = ["transductor", "start_date", "end_date"]
