from rest_framework import routers

from .views import TransductorModelViewSet

app_name = "transductor_models"

router = routers.DefaultRouter()
router.register(r'transductor_models', TransductorModelViewSet)

urlpatterns = []
