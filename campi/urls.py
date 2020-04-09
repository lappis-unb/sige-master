from .views import CampusViewSet

from rest_framework import routers


app_name = "campi"

router = routers.DefaultRouter()
router.register(r'campi', CampusViewSet)

urlpatterns = []
