import os
import numpy as np

from django.utils import timezone
from django.db.models.query import QuerySet

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.exceptions import APIException
from django.core.exceptions import ObjectDoesNotExist

from .models import *

from .serializers import VoltageRelatedEventSerializer
from .serializers import FailedConnectionSlaveEventSerializer
from .serializers import FailedConnectionTransductorEventSerializer
from .serializers import AllEventSerializer

from django.utils import timezone


class EventViewSet(mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = None
    model = None

    def get_queryset(self):
        type = self.request.query_params.get('type')
        transductor = self.request.query_params.get('transductor')

        if type == 'active':
            self.queryset = self.model.objects.filter(
                ended_at__isnull=True
            )
        elif type == 'inactive':
            self.queryset = self.model.objects.filter(
                ended_at__isnull=False
            )
        elif type == 'period':
            # Initially defined to be filtered for 3 days
            now = timezone.now()
            initial = now - timezone.timedelta(days=3)

            self.queryset = self.model.objects.filter(
                created_at__gte=initial,
                created_at__lte=now
            )
        else:
            self.queryset = self.model.objects.all()

        self.specific_query()

        return self.queryset

    def specific_query(self):
        pass


class VoltageRelatedEventViewSet(EventViewSet):
    model = VoltageRelatedEvent
    serializer_class = VoltageRelatedEventSerializer

    def specific_query(self):
        serial_number = self.request.query_params.get('serial_number')

        try:
            transductor = EnergyTransductor.objects.get(
                serial_number=serial_number
            )
            self.queryset = self.queryset.filter(
                transductor=transductor
            )
        except EnergyTransductor.DoesNotExist:
            raise APIException(
                'Serial number does not match with any transductor.'
            )


class FailedConnectionSlaveEventViewSet(EventViewSet):
    model = FailedConnectionSlaveEvent
    serializer_class = FailedConnectionSlaveEventSerializer

    def specific_query(self):
        ip_address = self.request.query_params.get('ip_address')

        try:
            slave = Slave.objects.get(ip_address=slave_ip)
            self.queryset = self.queryset.filter(
                slave=slave
            )
        except Slave.DoesNotExist:
            raise APIException(
                'IP Address does not match with any slave'
            )


class FailedConnectionTransductorEventViewSet(EventViewSet):
    model = FailedConnectionTransductorEvent
    serializer_class = FailedConnectionTransductorEventSerializer

    def specific_query(self):
        serial_number = self.request.query_params.get('serial_number')

        try:
            transductor = EnergyTransductor.objects.get(
                serial_number=serial_number
            )
            self.queryset = self.queryset.filter(
                transductor=transductor
            )
        except EnergyTransductor.DoesNotExist:
            raise APIException(
                'Serial number does not match with any transductor.'
            )


class AllEventsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = None
    serializer_class = AllEventSerializer
    types = {
        'FailedConnectionTransductorEvent': FailedConnectionTransductorEvent,
        'CriticalVoltageEvent': CriticalVoltageEvent,
        'PrecariousVoltageEvent': PrecariousVoltageEvent,
        'PhaseDropEvent': PhaseDropEvent
    }
    events = {
        'CriticalVoltageEvent': 'critical_tension',
        'PrecariousVoltageEvent': 'precarious_tension',
        'PhaseDropEvent': 'phase_drop',
        'FailedConnectionTransductorEvent': 'transductor_connection_fail'
    }

    def list(self, request):
        serial_number = request.data.get('serial_number')
        type = self.request.query_params.get('type')

        if type == 'period':
            # Initially defined to be filtered for 3 days
            now = timezone.now()
            initial = now - timezone.timedelta(days=3)

            self.queryset = Event.objects.filter(
                created_at__gte=initial,
                created_at__lte=now
            )
        else:
            self.queryset = Event.objects.filter(
                ended_at__isnull=True
            )

        if serial_number:
            try:
                self.queryset = self.queryset.filter(
                    transductor=EnergyTransductor.objects.get(
                        serial_number=serial_number
                    )
                )
            except EnergyTransductor.DoesNotExist:
                exception = APIException(
                    'Serial number does not match with any EnergyTransductor'
                )
                exception.status_code = 404
                raise exception

        events = {}

        for type in self.types:
            events[self.events[type]] = []
            elements = self.queryset.instance_of(self.types[type])
            for element in elements:
                event = {}
                event['id'] = element.pk
                event['location'] = element.transductor.name
                event['campus'] = element.transductor.campus.acronym
                event['transductor'] = element.transductor.serial_number
                event['data'] = element.data
                event['start_time'] = element.created_at
                event['end_time'] = element.ended_at
                events[self.events[type]].append(event)

        elements = self.queryset.instance_of(FailedConnectionSlaveEvent)

        slave_events = []

        for element in elements:
            transductors = (
                element.slave.transductors.select_related('campus').all()
            )
            for transductor in transductors:
                event = {}
                event['id'] = element.pk
                event['location'] = transductor.name
                event['campus'] = transductor.campus.acronym
                event['transductor'] = transductor.serial_number
                event['data'] = {'slave': element.slave.pk}
                event['start_time'] = element.created_at
                event['end_time'] = element.ended_at
                slave_events.append(event)

        events['slave_connection_fail'] = slave_events

        return Response(events, status=200)
