from rest_framework import serializers

from apps.memory_maps.models import MemoryMap


class MemoryMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryMap
        fields = (
            "id",
            "model",
            "instant_metrics",
            "cumulative_metrics",
            "created_at",
            "updated_at",

        )
        extra_kwargs = {
            "created_at": {"read_only": True},
        }
