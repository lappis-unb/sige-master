from rest_framework import serializers as s

from .models import FailedConnectionSlaveEvent
from .models import FailedConnectionTransductorEvent
from .models import VoltageRelatedEvent


class VoltageRelatedEventSerializer(s.HyperlinkedModelSerializer):
    class Meta:
        model = VoltageRelatedEvent
        fields = (
            'id',
            'measures',
            'created_at',
            'ended_at',
            'transductor'
        )


class FailedConnectionSlaveEventSerializer(s.HyperlinkedModelSerializer):
    class Meta:
        model = FailedConnectionSlaveEvent
        fields = (
            'id',
            'created_at',
            'ended_at',
            'slave'
        )


class FailedConnectionTransductorEventSerializer(s.HyperlinkedModelSerializer):
    class Meta:
        model = FailedConnectionTransductorEvent
        fields = (
            'id',
            'created_at',
            'ended_at',
            'transductor'
        )
