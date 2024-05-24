import logging

import pandas as pd
from django.db.models import Q
from django.db.models.functions import ExtractHour
from django.utils import timezone
from django_filters import rest_framework as filters

from .models import CumulativeMeasurement, InstantMeasurement

logger = logging.getLogger("apps.measurements.filters")


class BaseMeasurementFilter(filters.FilterSet):
    transductor = filters.NumberFilter(field_name="transductor")
    start_date = filters.DateTimeFilter(field_name="collection_date", lookup_expr="gte")
    end_date = filters.DateTimeFilter(field_name="collection_date", lookup_expr="lte")
    period = filters.CharFilter(method="filter_period")
    only_day = filters.BooleanFilter(method="filter_only_day")

    def filter_period(self, queryset, name, value):
        time_delta = pd.to_timedelta(value)
        start_date = timezone.now() - time_delta
        return queryset.filter(collection_date__gte=start_date)

    def filter_only_day(self, queryset, name, value):
        if value:
            # TODO: Validar se a conversão de timezone está buscando o horário correto
            start_hour_utc = 8  # 05:00 em São Paulo -> 08:00 UTC
            end_hour_utc = 22  # 19:00 em São Paulo -> 22:00 UTC

            queryset = queryset.annotate(hour=ExtractHour("collection_date")).filter(
                Q(hour__gte=start_hour_utc) & Q(hour__lt=end_hour_utc)
            )
        return queryset


class InstantMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = InstantMeasurement
        fields = ["transductor", "start_date", "end_date", "period", "only_day"]


class CumulativeMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = CumulativeMeasurement
        fields = ["transductor", "start_date", "end_date", "period", "only_day"]
