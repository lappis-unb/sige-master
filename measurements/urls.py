from .views import MinutelyMeasurementViewSet
from .views import QuarterlyMeasurementViewSet
from .views import MonthlyMeasurementViewSet

from rest_framework import routers


app_name = "minutely_measurements"

router = routers.DefaultRouter()
router.register(r'minutely_measurements', MinutelyMeasurementViewSet)
router.register(r'quarterly_measurements', QuarterlyMeasurementViewSet)
router.register(r'monthly_measurements', MonthlyMeasurementViewSet)

urlpatterns = []
