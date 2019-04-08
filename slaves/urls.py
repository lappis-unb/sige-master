from .views import SlaveViewSet

from rest_framework import routers


app_name = "slaves"

router = routers.DefaultRouter()
router.register(r'slaves', SlaveViewSet)

urlpatterns = []