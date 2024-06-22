import logging

from rest_framework import viewsets

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
)
from apps.events.serializers import (
    CumulativeMeasurementTriggerSerializer,
    EventSerializer,
    InstantMeasurementTriggerSerializer,
)

logger = logging.getLogger("apps.events.views")


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class InstantMeasurementTriggerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurementTrigger.objects.all()
    serializer_class = InstantMeasurementTriggerSerializer


class CumulativeMeasurementTriggerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CumulativeMeasurementTrigger.objects.all()
    serializer_class = CumulativeMeasurementTriggerSerializer
