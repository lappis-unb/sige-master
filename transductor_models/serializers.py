from rest_framework import serializers

from .models import TransductorModel


class TransductorModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransductorModel
        fields = ('model_code', 'name', 'serial_protocol', 'transport_protocol', 'minutely_register_addresses', 'quarterly_register_addresses', 'monthly_register_addresses', 'url')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update()

        return instance
