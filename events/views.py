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
from campi.models import Campus

from .serializers import VoltageRelatedEventSerializer
from .serializers import FailedConnectionSlaveEventSerializer
from .serializers import FailedConnectionTransductorEventSerializer
from .serializers import AllEventSerializer

from django.utils import timezone
from django.db.models import Q


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
        transductor_id = self.request.query_params.get('id')

        try:
            transductor = EnergyTransductor.objects.get(
                id=transductor_id
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
        slave_id = self.request.query_params.get('slave')

        try:
            slave = Slave.objects.get(pk=slave_id)
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
        transductor_id = self.request.query_params.get('id')

        try:
            transductor = EnergyTransductor.objects.get(
                id=transductor_id
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
        'CriticalVoltageEvent': CriticalVoltageEvent,
        'PrecariousVoltageEvent': PrecariousVoltageEvent,
        'PhaseDropEvent': PhaseDropEvent
    }
    events = {
        'CriticalVoltageEvent': 'critical_tension',
        'PrecariousVoltageEvent': 'precarious_tension',
        'PhaseDropEvent': 'phase_drop'
    }

    def list(self, request):
        transductor_id = self.request.query_params.get('id')
        type = self.request.query_params.get('type')
        campus = self.request.query_params.get('campus')

        if type == 'period':
            # Initially defined to be filtered for 3 days
            now = timezone.now()
            initial = now - timezone.timedelta(days=3)

            voltage_related_events = self.generic_filter(
                VoltageRelatedEvent,
                (initial, now),
                type
            )

            failed_connection_transductor_events = self.generic_filter(
                FailedConnectionTransductorEvent,
                (initial, now),
                type
            )

            failed_connection_slave_events = self.generic_filter(
                FailedConnectionSlaveEvent,
                (initial, now),
                type
            )

        else:
            voltage_related_events = self.generic_filter(
                VoltageRelatedEvent
            )

            failed_connection_transductor_events = self.generic_filter(
                FailedConnectionTransductorEvent
            )

            failed_connection_slave_events = self.generic_filter(
                FailedConnectionSlaveEvent
            )

        if transductor_id:
            try:
                transductor = EnergyTransductor.objects.get(
                    id=transductor_id
                )

                voltage_related_events = voltage_related_events.filter(
                    transductor=transductor
                )

                failed_connection_transductor_events = (
                    failed_connection_transductor_events.filter(
                        transductor=transductor
                    )
                )

                failed_connection_slave_events = (
                    failed_connection_slave_events.filter(
                        slave__transductors__in=[transductor]
                    )
                )
            except EnergyTransductor.DoesNotExist:
                exception = APIException(
                    'Energy transductor id does not match '
                    'with any EnergyTransductor'
                )
                exception.status_code = 404
                raise exception
        elif campus:
            try:
                transductors = EnergyTransductor.objects.filter(
                    campus=Campus.objects.get(pk=int(campus))
                )

                voltage_related_events = voltage_related_events.filter(
                    transductor__in=transductors
                )
                failed_connection_transductor_events = (
                    failed_connection_transductor_events.filter(
                        transductor__in=transductors
                    )
                )
                failed_connection_slave_events = (
                    failed_connection_slave_events.filter(
                        slave__transductors__in=transductors
                    )
                )
            except Campus.DoesNotExist:
                exception = APIException(
                    'Campus id does not match with any Campus'
                )
                exception.status_code = 404
                raise exception

        events = {}

        for type in self.types:
            events[self.events[type]] = []
            elements = voltage_related_events.instance_of(self.types[type])
            self.build_transductor_related_event(
                events, elements, self.events[type]
            )

        events['transductor_connection_fail'] = []
        self.build_transductor_related_event(
            events, failed_connection_transductor_events, 
            'transductor_connection_fail'
        )

        slave_events = []

        for element in failed_connection_slave_events:
            if transductor_id:
                transductors = (
                    element.slave.transductors.select_related('campus').filter(
                        pk=transductor_id
                    )
                )
            else:
                transductors = (
                    element.slave.transductors.select_related('campus').all()
                )
            for transductor in transductors:
                event = {}
                event['id'] = element.pk
                event['location'] = transductor.name
                event['campus'] = transductor.campus.acronym
                event['transductor'] = transductor.id
                event['data'] = {'slave': element.slave.pk}
                event['start_time'] = element.created_at
                event['end_time'] = element.ended_at
                slave_events.append(event)

        events['slave_connection_fail'] = slave_events

        events['count'] = \
            len(events['slave_connection_fail']) \
            + len(events['transductor_connection_fail']) \
            + len(events['phase_drop']) \
            + len(events['critical_tension'])

        events['critical_events_count'] = \
            len(events['critical_tension']) \
            + len(events['phase_drop'])

        events['light_events_count'] = \
            len(events['slave_connection_fail']) \
            + len(events['transductor_connection_fail']) \
            + len(events['precarious_tension'])

        return Response(events, status=200)

    def generic_filter(self, class_instance, range=None, period=None):
        queryset = None

        if period is not None and range is not None:
            queryset = class_instance.objects.filter(
                Q(ended_at__isnull=True) | Q(ended_at__range=range)
            )
        else:
            queryset = class_instance.objects.filter(
                ended_at__isnull=True
            )

        return queryset

    def build_transductor_related_event(self, events, elements, type):
        for element in elements:
            event = {}
            event['id'] = element.pk
            event['location'] = element.transductor.name
            event['campus'] = element.transductor.campus.acronym
            event['transductor'] = element.transductor.serial_number
            event['data'] = element.data
            event['start_time'] = element.created_at
            event['end_time'] = element.ended_at
            events[type].append(event)
