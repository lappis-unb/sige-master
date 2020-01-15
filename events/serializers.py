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


class AllEventSerializer(serializers.HyperlinkedModelSerializer):
    communication_fail = serializers.ListField(child=serializers.DictField())
    critical_tension = serializers.ListField(child=serializers.DictField())
    precarious_tension = serializers.ListField(child=serializers.DictField())
    phase_drop = serializers.ListField(child=serializers.DictField())
    # energy_drop = serializers.ListField(child=serializers.DictField())
    consumption_peak = serializers.ListField(child=serializers.DictField())
    consumption_above_contract = serializers.ListField(
        child=serializers.DictField()
    )

    class Meta:
        model = Event
        fields = (
            'critical_tension',
            'precarious_tension',
            'phase_drop',
            'communication_fail',
            # 'energy_drop',
            'consumption_peak',
            'consumption_above_contract'
        )
