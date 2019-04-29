from .views import MinutlyMeasurementsViewSet

from rest_framework import routers


app_name = "minutly_measurements"

router = routers.DefaultRouter()
router.register(r'minutly_measurements', MinutlyMeasurementsViewSet)

urlpatterns = []
