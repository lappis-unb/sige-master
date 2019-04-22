from rest_framework import serializers

from .models import TransductorModel


class TransductorModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransductorModel
        fields = ('name', 'serial_protocol', 'transport_protocol')
