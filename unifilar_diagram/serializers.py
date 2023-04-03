from rest_framework import serializers

from .models import Line


class LineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Line
        fields = (
            'id',
            'start_lat',
            'start_lng',
            'end_lat',
            'end_lng',
            'campus'
        )
