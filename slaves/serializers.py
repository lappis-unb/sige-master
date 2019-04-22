from rest_framework import serializers

from .models import Slave

class SlaveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Slave
        fields = ('id', 'ip_address', 'location', 'url')