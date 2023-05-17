from rest_framework import permissions, viewsets

from users.permissions import CurrentADMINUserOnly

from .models import Group, GroupType
from .serializers import GroupSerializer, GroupTypeSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,)


class GroupTypeViewSet(viewsets.ModelViewSet):
    queryset = GroupType.objects.all()
    serializer_class = GroupTypeSerializer
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,)
