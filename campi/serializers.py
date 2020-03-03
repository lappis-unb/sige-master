from rest_framework import serializers

from .models import Campus


class CampusSerializer(serializers.HyperlinkedModelSerializer):
    transductors = serializers.IntegerField(
        source='energytransductor_set.count', read_only=True
    )

    class Meta:
        model = Campus
        fields = (
            'id',
            'name',
            'acronym',
            'transductors',
            'url'
        )
