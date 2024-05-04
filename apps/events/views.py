import logging

from rest_framework import viewsets

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
    Trigger,
)
from apps.events.serializers import (
    CumulativeMeasurementTriggerSerializer,
    EventTypeSerializer,
    InstantMeasurementTriggerSerializer,
    TriggerSerializer,
)

logger = logging.getLogger("apps.events.views")


class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventTypeSerializer


class TriggerViewSet(viewsets.ModelViewSet):
    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer


class InstantMeasurementTriggerViewSet(viewsets.ModelViewSet):
    queryset = InstantMeasurementTrigger.objects.all()
    serializer_class = InstantMeasurementTriggerSerializer


class CumulativeMeasurementTriggerViewSet(viewsets.ModelViewSet):
    queryset = CumulativeMeasurementTrigger.objects.all()
    serializer_class = CumulativeMeasurementTriggerSerializer
