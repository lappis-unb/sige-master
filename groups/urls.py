from rest_framework import routers
from .views import GroupViewSet
from .views import GroupTypeViewSet

router = routers.DefaultRouter()
router.register(
    r'groups',
    GroupViewSet
)
router.register(
    r'group-types',
    GroupTypeViewSet
)
