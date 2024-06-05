from rest_framework import routers

from .views import LineViewSet

app_name = "lines"

router = routers.DefaultRouter()
router.register(r"lines", LineViewSet, basename="lines")

urlpatterns = []
