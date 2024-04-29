import logging

from django.db.models import Prefetch
from rest_framework import viewsets

from apps.events.models import Event, MeasurementTrigger
from apps.events.serializers import (
    EventSerializer,
    EventTypeSerializer,
    MeasurementTriggerSerializer,
)

logger = logging.getLogger("apps.events.views")


class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventTypeSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    # queryset = Event.objects.select_related("measurement_trigger").all()
    serializer_class = EventSerializer

    def get_queryset(self):
        measurement_triggers = MeasurementTrigger.objects.select_related("eventtrigger_ptr")

        return Event.objects.prefetch_related(
            Prefetch(
                "measurement_trigger",
                queryset=measurement_triggers,
            )
        )


class MeasurementTriggerViewSet(viewsets.ModelViewSet):
    queryset = MeasurementTrigger.objects.all()
    serializer_class = MeasurementTriggerSerializer
