from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from rest_framework.status import HTTP_409_CONFLICT
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from .serializers import *
from .models import CustomUser

class CurrentUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        userid = request.path.split('/')
        userid = userid[2]
        try:
            userid = int(userid)
        except Exception:
            return False
        return request.user == CustomUser.objects.get(id=userid)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser|CurrentUserOnly]
