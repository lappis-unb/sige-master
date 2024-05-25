import logging

import dateutil
from django.utils import timezone
from pandas import Timestamp
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


class GraphDataSerializer(serializers.Serializer):
    information = serializers.SerializerMethodField()
    timestamp = serializers.ListField(child=serializers.CharField(), allow_null=True)
    traces = serializers.ListField(child=serializers.DictField(), allow_null=True)

    def get_information(self, instance):
        tz = timezone.get_current_timezone()
        return {
            "time_zone": f"{tz.key} (UTC{tz.tzname(instance.collection_date.min())})",
            "date_format": "ISO-8601",
            "start_date": instance.collection_date.min().astimezone(tz),
            "end_date": instance.collection_date.max().astimezone(tz),
            "count": len(instance),
            "fields": [field for field in instance.columns if field != "collection_date"],
        }

    def get_timestamp(self, instance):
        tz = timezone.get_current_timezone()
        return instance.collection_date.apply(lambda ts: ts.astimezone(tz).isoformat()).tolist()

    def get_traces(self, instance):
        traces = []
        for field in instance["information"]["fields"]:
            field_data = {
                "field": field,
                "avg_value": instance[field].mean().round(2),
                "max_value": instance[field].max(),
                "min_value": instance[field].min(),
                "values": instance[field].tolist(),
            }
            traces.append(field_data)
        return traces

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        tz = timezone.get_current_timezone()
        timestamp = instance.collection_date.apply(lambda ts: ts.astimezone(tz))
        rep["timestamp"] = timestamp.tolist()

        traces = []
        for field in rep["information"]["fields"]:
            field_data = {
                "field": field,
                "avg_value": instance[field].mean().round(2),
                "max_value": instance[field].max(),
                "min_value": instance[field].min(),
                "values": instance[field].tolist(),
            }
            traces.append(field_data)
        rep["traces"] = traces
        return rep
