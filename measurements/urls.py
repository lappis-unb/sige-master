from .views import MinutlyMeasurementsViewSet, QuarterlyMeasurementViewSet

from rest_framework import routers


app_name = "minutly_measurements"

router = routers.DefaultRouter()
router.register(r'minutly_measurements', MinutlyMeasurementsViewSet)
router.register(r'quarterly_measurements', QuarterlyMeasurementViewSet)

urlpatterns = []
