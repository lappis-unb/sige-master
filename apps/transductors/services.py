from django.db.models import Count, Q, Sum

from apps.transductors.models import Status


def calculate_aggregation_status(queryset, transductor):
    aggregation = queryset.aggregate(
        total_broken=Count("id", filter=Q(status=Status.BROKEN)),
        total_disabled=Count("id", filter=Q(status=Status.DISABLED)),
        total_maintenance=Count("id", filter=Q(status=Status.MAINTENANCE)),
        total_other=Count("id", filter=Q(status=Status.OTHER)),
        downtime=Sum("duration", filter=Q(status=Status.BROKEN)),
        uptime=Sum("duration", filter=Q(status=Status.ACTIVE)),
    )

    total_time = aggregation["downtime"] + aggregation["uptime"]
    downtime_percent = round((aggregation["downtime"] / total_time * 100) if total_time else 0, 2)
    uptime_percent = round((aggregation["uptime"] / total_time * 100) if total_time else 0, 2)

    return {
        "transductor": transductor.id,
        "ip_address": transductor.ip_address,
        "status_summary": {
            "broken_status_count": aggregation["total_broken"],
            "disabled_status_count": aggregation["total_disabled"],
            "maintenance_status_count": aggregation["total_maintenance"],
            "other_status_count": aggregation["total_other"],
        },
        "time_summary": {
            "downtime_seconds": aggregation["downtime"],
            "uptime_seconds": aggregation["uptime"],
            "downtime_percent": downtime_percent,
            "uptime_percent": uptime_percent,
        },
        "current_status": {
            "status": transductor.current_status.get_status_display(),
            "uptime": transductor.uptime,
            "start_time": transductor.current_status.start_time,
            "notes": transductor.current_status.notes,
        },
    }
