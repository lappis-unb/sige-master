from rest_framework import viewsets
from rest_framework import permissions
from .models import Group
from .models import GroupType
from .serializers import GroupSerializer
from .serializers import GroupTypeSerializer

from users.permissions import CurrentADMINUserOnly


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # Para testes de Admin, retirar os permissions.AllowAny
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,)


class GroupTypeViewSet(viewsets.ModelViewSet):
    queryset = GroupType.objects.all()
    serializer_class = GroupTypeSerializer
    # Para testes de Admin, retirar os permissions.AllowAny
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,)
