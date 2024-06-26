import logging

from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.events.models import (
    CategoryTrigger,
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
    SeverityTrigger,
)
from apps.events.pagination import EventPagination
from apps.events.serializers import (
    CumulativeMeasurementTriggerSerializer,
    EventSerializer,
    InstantMeasurementTriggerSerializer,
)
from apps.events.services import calculate_aggregation_events
from apps.transductors.models import Transductor

logger = logging.getLogger("apps.events.views")


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination

    @action(methods=["get"], detail=False)
    def summary(self, request):
        queryset = self.get_queryset()
        aggregations = {"total_events": Count("id"), "open_events": Count("id", filter=Q(is_active=False))}

        for severity in SeverityTrigger:
            severity_key = f"total_{severity.label.lower()}"
            aggregations[severity_key] = Count("id", filter=Q(trigger__severity=severity.value))

        for category in CategoryTrigger:
            category_key = f"total_{category.label.lower()}"
            aggregations[category_key] = Count("id", filter=Q(trigger__category=category.value))

        aggregation = queryset.aggregate(**aggregations)

        category_summary = {
            category.label.lower(): aggregation[f"total_{category.label.lower()}"] for category in CategoryTrigger
        }

        severity_summary = {
            severity.label.lower(): aggregation[f"total_{severity.label.lower()}"] for severity in SeverityTrigger
        }

        transductors_summary = []
        for transductor in Transductor.objects.all():
            event_qs = Event.objects.filter(transductor=transductor)
            event_summary = calculate_aggregation_events(event_qs, transductor)
            transductors_summary.append(event_summary)

        response_data = {
            "general_events_summary": {
                "total_events": aggregation["total_events"],
                "open_events": aggregation["open_events"],
                "category_summary": category_summary,
                "severity_summary": severity_summary,
            },
            "transductors_events_summary": transductors_summary,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class InstantMeasurementTriggerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurementTrigger.objects.all()
    serializer_class = InstantMeasurementTriggerSerializer


class CumulativeMeasurementTriggerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CumulativeMeasurementTrigger.objects.all()
    serializer_class = CumulativeMeasurementTriggerSerializer
