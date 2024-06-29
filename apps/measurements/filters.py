import logging

from django.db.models import Q
from django.db.models.functions import ExtractHour
from django_filters import rest_framework as filters

from .models import CumulativeMeasurement, InstantMeasurement

logger = logging.getLogger("apps.measurements.filters")


class BaseMeasurementFilter(filters.FilterSet):
    transductor = filters.NumberFilter(field_name="transductor")
    start_date = filters.DateTimeFilter(field_name="collection_date", lookup_expr="gte")
    end_date = filters.DateTimeFilter(field_name="collection_date", lookup_expr="lte")
    only_day = filters.BooleanFilter(method="filter_only_day")

    def filter_only_day(self, queryset, name, value):
        if value:
            # TODO: Validar se a conversão de timezone está buscando o horário correto
            start_hour = 6  # 06:00 em São Paulo -> 09:00 UTC
            end_hour = 19  # 19:00 em São Paulo -> 22:00 UTC

            queryset = queryset.annotate(hour=ExtractHour("collection_date")).filter(
                Q(hour__gte=start_hour) & Q(hour__lt=end_hour)
            )
        return queryset


class InstantMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = InstantMeasurement
        fields = ["transductor", "start_date", "end_date", "only_day"]


class CumulativeMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = CumulativeMeasurement
        fields = ["transductor", "start_date", "end_date", "only_day"]


class DailyProfileFilter(BaseMeasurementFilter):
    only_day = None
    peak_hours = filters.BooleanFilter(method="filter_peak_hours")
    off_peak_hours = filters.BooleanFilter(method="filter_off_peak_hours")

    class Meta:
        model = CumulativeMeasurement
        fields = [
            "transductor",
            "start_date",
            "end_date",
            "peak_hours",
            "off_peak_hours",
        ]

    def filter_off_peak_hours(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(hour=ExtractHour("collection_date")).exclude(
                Q(hour__gte=18) & Q(hour__lt=21),
            )
        return queryset

    def filter_peak_hours(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(hour=ExtractHour("collection_date")).filter(
                Q(hour__gte=18) & Q(hour__lt=21),
            )
        return queryset
