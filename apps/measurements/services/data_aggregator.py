from django.conf import settings
from django.db.models import Case, Count, Max, Min, Q, Sum, When


class ReportDataAggregator:
    def __init__(self) -> None:
        self.setup()

    def setup(self):
        self.base_aggregations = {
            "start_date": Min("collection_date"),
            "end_date": Max("collection_date"),
            "total_measurements": Count("id"),
        }

    def get_filter_condition(self):
        return (
            Q(collection_date__time__gte=settings.PEAK_TIME_START)
            & Q(collection_date__time__lte=settings.PEAK_TIME_END)
            & Q(collection_date__iso_week_day__lte=5)
        )

    def perform_aggregation(self, queryset, fields, detail=False):
        filter_conditions = self.get_filter_condition()
        annotations = self.prepare_annotations(fields, filter_conditions, self.base_aggregations)

        if detail:
            return queryset.values("transductor").annotate(**annotations)
        else:
            return queryset.aggregate(**annotations)

    def prepare_annotations(self, fields, filter_conditions, aggregations):
        annotations = dict(aggregations)

        for field in fields:
            annotations[f"{field}_peak"] = Sum(field, filter=filter_conditions)
            annotations[f"{field}_off_peak"] = Sum(field, filter=~filter_conditions)
        return annotations
