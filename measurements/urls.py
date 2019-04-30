from .views import MinutelyMeasurementsViewSet, QuarterlyMeasurementViewSet

from rest_framework import routers


app_name = "minutely_measurements"

router = routers.DefaultRouter()
router.register(r'minutely_measurements', MinutelyMeasurementsViewSet)
router.register(r'quarterly_measurements', QuarterlyMeasurementViewSet)

urlpatterns = []
