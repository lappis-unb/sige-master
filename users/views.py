from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from rest_framework.status import HTTP_409_CONFLICT
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from users import models
from users import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdminUser,)
