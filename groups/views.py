from rest_framework import viewsets
from rest_framework import permissions
from .models import Group
from .models import GroupType
from .serializers import GroupSerializer
from .serializers import GroupTypeSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.AllowAny,)


class GroupTypeViewSet(viewsets.ModelViewSet):
    queryset = GroupType.objects.all()
    serializer_class = GroupTypeSerializer
    permission_classes = (permissions.AllowAny,)
