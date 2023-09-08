from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework.exceptions import APIException

from campi.models import Campus
from groups.models import Group
from measurements.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    RealTimeMeasurement,
)


class BaseMeasurementFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name="transductor")
    campus = filters.NumberFilter(method="filter_campus", field_name="campus")
    group = filters.NumberFilter(method="filter_group", field_name="grouping")
    start_date = filters.DateTimeFilter(method="filter_start_date", field_name="collection_date", lookup_expr="gte")
    end_date = filters.DateTimeFilter(method="filter_end_date", field_name="collection_date", lookup_expr="lte")

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(collection_date__gte=value) if value else queryset

    def filter_end_date(self, queryset, name, value):
        if not value:
            value = timezone.now()
        return queryset.filter(collection_date__lte=value)

    def filter_campus(self, queryset, name, value):
        try:
            campus = Campus.objects.get(pk=int(value))
            return queryset.filter(transductor__campus=campus)
        except Campus.DoesNotExist:
            raise APIException("Campus id does not match with any existent campus.")

    def filter_group(self, queryset, name, value):
        try:
            group = Group.objects.get(pk=int(value))
            return queryset.filter(transductor__grouping=group)
        except Group.DoesNotExist:
            raise APIException("Group id does not match with any existent group.")


class MinutelyMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        fields = ["id", "start_date", "end_date"]
        model = MinutelyMeasurement


class UferMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        fields = fields = ["start_date", "end_date", "campus", "group"]
        model = MinutelyMeasurement


class QuarterlyMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = QuarterlyMeasurement
        fields = ["id", "start_date", "end_date", "campus", "group"]


class MonthlyMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        fields = ["id", "start_date", "end_date"]
        model = MonthlyMeasurement


class RealTimeMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        fields = ["id"]
        model = RealTimeMeasurement
