from .views import LineViewSet

from rest_framework import routers


app_name = "lines"

router = routers.DefaultRouter()
router.register(r'lines', LineViewSet, basename='lines')

urlpatterns = []
