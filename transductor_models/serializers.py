from rest_framework import serializers

from .models import TransductorModel


class TransductorModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransductorModel
        fields = ('model_code', 'name', 'serial_protocol', 'transport_protocol', 'minutely_register_addresses', 'quarterly_register_addresses', 'monthly_register_addresses', 'url')
