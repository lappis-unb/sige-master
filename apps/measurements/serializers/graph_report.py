import logging

from django.utils import timezone
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from apps.measurements.serializers.utils import (
    daily_profile_hourly_example,
    energy_report_example,
    graph_data_example,
    ufer_report_example,
)
from apps.transductors.models import Transductor

logger = logging.getLogger("apps.measurements.serializers.graph_report")


@extend_schema_serializer(examples=[ufer_report_example])
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


@extend_schema_serializer(examples=[energy_report_example])
class ReportSummarySerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_dynamic_fields()

    def add_dynamic_fields(self):
        fields = self.context.get("fields", [])
        if fields:
            for field in fields:
                self.fields[field] = serializers.FloatField()


@extend_schema_serializer(examples=[energy_report_example])
class ReportDetailSerializer(serializers.Serializer):
    transductor = serializers.IntegerField()
    total_measurements = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_dynamic_fields()

    def add_dynamic_fields(self):
        fields = self.context.get("fields", [])
        if fields:
            for field in fields:
                self.fields[field] = serializers.FloatField()

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


@extend_schema_serializer(examples=[daily_profile_hourly_example])
class DailyProfileSerializer(serializers.Serializer):
    time = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_dynamic_fields()

    def add_dynamic_fields(self):
        fields = self.context.get("fields", [])
        if fields:
            for field in fields:
                self.fields[field] = serializers.FloatField()

    def get_time(self, obj):
        hour = obj.get("hour", 0)
        minute = obj.get("minute", 0)
        second = obj.get("second", 0)
        return f"{hour:02}:{minute:02}:{second:02}"


@extend_schema_serializer(examples=[graph_data_example])
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
