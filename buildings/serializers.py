from rest_framework import serializers
from .models import Building


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Building
        fields = (
            'id',
            'name',
            'phone',
            'acronym',
            'campus',
            'url',
        )
