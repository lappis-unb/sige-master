from rest_framework import serializers

from .models import Slave


class SlaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slave
        fields = (
            "id",
            "name",
            "server_address",
            "port",
            "broken",
            "active",
        )
        read_only_fields = ["broken"]
