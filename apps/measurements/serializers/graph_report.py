import logging

import dateutil
from django.utils import timezone
from rest_framework import serializers

from apps.transductors.models import Transductor

logger = logging.getLogger("apps")


class UferSerializer(serializers.Serializer):
    total_measurements = serializers.IntegerField()
    transductor = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(UferSerializer, self).__init__(*args, **kwargs)
        fields = self.context.get("fields", [])
        for field in fields:
            self.fields[f"pf_phase_{field[-1]}"] = serializers.FloatField(required=False)

    def to_representation(self, instance):
        transductor = (
            Transductor.objects.filter(pk=instance["transductor"])
            .values("located__acronym", "located__name", "ip_address")
            .first()
        )
        rep = {
            "located": f"{transductor['located__acronym']} - {transductor['located__name']}",
            "ip_address": transductor["ip_address"],
        }
        rep.update(super().to_representation(instance))
        return rep


class ReportSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs["context"].get("fields", [])
        super(ReportSerializer, self).__init__(*args, **kwargs)

        for field_name in fields:
            if field_name not in self.fields:
                self.fields[field_name] = serializers.FloatField(allow_null=True)


class DetailDailySerializer(serializers.Serializer):
    time = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        fields = kwargs["context"].get("fields", [])
        super(DetailDailySerializer, self).__init__(*args, **kwargs)

        if fields:
            for field in fields:
                self.fields[field] = serializers.FloatField()

    def get_time(self, obj):
        time = f"{obj['hour']}:{obj['minute']}"
        return dateutil.parser.parse(time).time()


class GraphDataSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        """
        Format data for graph representation
        Example:
        {
            "information": {
                "time_zone": "America/Sao_Paulo",
                "date_format": "ISO-8601",
                "count": 4,
                "fields": ["voltage_a", "voltage_b", "voltage_c"]
            },

            "timestamp": ["2024-05-01T00:00:00.000Z", "2024-05-01T00:05:00.000Z", ...],
            "traces": [
                {
                    "field": "voltage_a",
                    "avg_value": 222.68,
                    "max_value": 227.05,
                    "min_value: 217.48,
                    "values": [
                        219.32,
                        227.05,
                        217.48
                    ]
                },
                {
                    "field": "voltage_b",
                    "count": 4,
                    "avg": 222.2,
                    "max_value": 226.27,
                    "min_value": 217.06,
                    "values": [
                        226.21,
                        226.27,
                        217.06
                    ]
                },
                ....
            ],
        }
        """
        tz = timezone.get_current_timezone()
        response = {
            "information": {
                "time_zone": timezone.get_current_timezone_name(),
                "date_format": "ISO-8601",
                "start_date": instance.collection_date.min().astimezone(tz).isoformat(),
                "end_date": instance.collection_date.max().astimezone(tz).isoformat(),
                "count": instance.shape[0],
                "fields": [field for field in instance.columns if field != "collection_date"],
            },
            "timestamp": [],
            "traces": [],
        }

        timestamp = instance.collection_date.apply(lambda ts: ts.astimezone(tz).isoformat())
        response["timestamp"] = timestamp.tolist()

        for field in response["information"]["fields"]:
            response["traces"].append(
                {
                    "field": field,
                    "avg_value": instance[field].mean().round(2),
                    "max_value": instance[field].max(),
                    "min_value": instance[field].min(),
                    "values": instance[field].tolist(),
                }
            )
        return response
