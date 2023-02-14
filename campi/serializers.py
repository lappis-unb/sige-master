from rest_framework import serializers

from .models import Campus, Tariff
from groups.models import Group
from transductors.models import EnergyTransductor


class CampusSerializer(serializers.HyperlinkedModelSerializer):
    transductors = serializers.IntegerField(
        source='energytransductor_set.count', read_only=True
    )
    groups_related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Campus
        fields = (
            'id',
            'name',
            'acronym',
            'transductors',
            'geolocation_latitude',
            'geolocation_longitude',
            'zoom_ratio',
            'groups_related',
            'url',
            'contract_type',
            'off_peak_demand',
            'peak_demand'
        )

    def get_groups_related(self, obj):
        campus = Campus.objects.get(
            pk=obj.__dict__['id']
        )
        transductors = EnergyTransductor.objects.filter(
            campus__in=[campus]
        )
        groups = Group.objects.filter(
            energytransductor__in=transductors
        )

        response = []

        for group in groups:
            data = {}
            data['id'] = group.pk
            data['name'] = group.name
            response.append(data)

        return response


class TariffSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tariff
        fields = (
            'id',
            'start_date',
            'campus',
            'regular_tariff',
            'high_tariff'
        )
