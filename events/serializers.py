from rest_framework import serializers as s

from .models import FailedConnectionSlaveEvent
from .models import FailedConnectionTransductorEvent
from .models import VoltageRelatedEvent
from .models import Event


class VoltageRelatedEventSerializer(s.HyperlinkedModelSerializer):
    class Meta:
        model = VoltageRelatedEvent
        fields = (
            'id',
            'data',
            'created_at',
            'ended_at',
            'transductor'
        )


class FailedConnectionSlaveEventSerializer(s.HyperlinkedModelSerializer):
    class Meta:
        model = FailedConnectionSlaveEvent
        fields = (
            'id',
            'data',
            'created_at',
            'ended_at',
            'slave'
        )


class FailedConnectionTransductorEventSerializer(s.HyperlinkedModelSerializer):
    class Meta:
        model = FailedConnectionTransductorEvent
        fields = (
            'id',
            'data',
            'created_at',
            'ended_at',
            'transductor'
        )


class AllEventSerializer(s.HyperlinkedModelSerializer):
    slave_connection_fail = s.ListField(child=s.DictField())
    transductor_connection_fail = s.ListField(child=s.DictField())
    critical_tension = s.ListField(child=s.DictField())
    precarious_tension = s.ListField(child=s.DictField())
    phase_drop = s.ListField(child=s.DictField())

    class Meta:
        model = Event
        fields = (
            'critical_tension',
            'precarious_tension',
            'phase_drop',
            'slave_connection_fail',
            'transductor_connection_fail'
        )
