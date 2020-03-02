from rest_framework import serializers

from .models import Campus


class CampusSerializer(serializers.HyperlinkedModelSerializer):
    transductors = serializers.IntegerField(default=0)

    class Meta:
        model = Campus
        fields = (
            'id',
            'name',
            'acronym',
            'transductors',
            'url'
        )
