from rest_framework import serializers

from .models import Campus


class CampusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campus
        fields = ('id', 'name', 'acronym')
