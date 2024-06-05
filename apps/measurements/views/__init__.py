from .base import CumulativeMeasurementViewSet, InstantMeasurementViewSet
from .graph import CumulativeGraphViewSet, DailyProfileViewSet, InstantGraphViewSet
from .report import ReportViewSet, UferViewSet

__all__ = [
    "CumulativeMeasurementViewSet",
    "InstantMeasurementViewSet",
    "CumulativeGraphViewSet",
    "InstantGraphViewSet",
    "ReportViewSet",
    "UferViewSet",
    "DailyProfileViewSet",
]
