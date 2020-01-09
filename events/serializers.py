from rest_framework import serializers

from .models import FailedConnectionSlaveEvent
from .models import FailedConnectionTransductorEvent
from .models import VoltageRelatedEvent


class VoltageRelatedEventSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = VoltageRelatedEvent
        fields = (
            'id',
            'measures',
            'transductor',
        )


class FailedConnectionSlaveEvent(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FailedConnectionSlaveEvent
        fields = (
            'id',
            'created_at',
            'ended_at',
            'slave'
        )


class FailedConnectionTransductorEvent(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FailedConnectionTransductorEvent
        fields = (
            'id',
            'created_at',
            'ended_at',
            'transductor'
        )
