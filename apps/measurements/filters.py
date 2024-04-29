from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework.exceptions import APIException

from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.organizations.models import Entity


class BaseMeasurementFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name="transductor")
    entity = filters.NumberFilter(method="filter_entity", field_name="entity")
    start_date = filters.DateTimeFilter(method="filter_start_date", field_name="created", lookup_expr="gte")
    end_date = filters.DateTimeFilter(method="filter_end_date", field_name="created", lookup_expr="lte")

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(created__gte=value) if value else queryset

    def filter_end_date(self, queryset, name, value):
        if not value:
            value = timezone.now()
        return queryset.filter(created__lte=value)

    def filter_entity(self, queryset, name, value):
        try:
            entity = Entity.objects.get(pk=int(value))
            return queryset.filter(transductor__entity=entity)
        except Entity.DoesNotExist:
            raise APIException("Entity id does not match with any existent Organization.")


class InstantMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        fields = ["id", "start_date", "end_date"]
        model = InstantMeasurement


class CumulativeMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        model = CumulativeMeasurement
        fields = ["id", "start_date", "end_date", "entity"]


class UferMeasurementFilter(BaseMeasurementFilter):
    class Meta:
        fields = fields = ["start_date", "end_date", "entity"]
        model = InstantMeasurement
