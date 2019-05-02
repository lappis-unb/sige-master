from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from rest_framework.status import HTTP_409_CONFLICT
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from .models import *
from .serializers import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

    # def create(self, request):
    #     permission_classes = (permissions.AllowAny,)
    #     new_user, created = User.objects.get_or_create(request.data)
    #     serializer = UserSerializer(new_user)
    #     if created:
    #         return Response(serializer.data)
    #     else:
    #         return Response(HTTP_409_CONFLICT)


class ResearcherUserViewSet(viewsets.ModelViewSet):
    queryset = ResearcherUser.objects.all()
    serializer_class = ResearcherUserSerializer
    permission_classes = (permissions.IsAdminUser,)

    # def create(self, request):
    #     permission_classes = (permissions.AllowAny,)
    #     new_user, created = User.objects.get_or_create(request.data)
    #     serializer = ResearcherUserSerializer(new_user)
    #     if created:
    #         return Response(serializer.data)
    #     else:
    #         return Response(HTTP_409_CONFLICT)


class ManagerUserViewSet(viewsets.ModelViewSet):
    queryset = ManagerUser.objects.all()
    serializer_class = ManagerUserSerializer
    permission_classes = (permissions.IsAdminUser,)

    # def create(self, request):
    #     # permission_classes = (permissions.AllowAny,)
    #     new_user, created = User.objects.get_or_create(request.data)
    #     serializer = ManagerUserSerializer(new_user)
    #     if created:
    #         return Response(serializer.data)
    #     else:
    #         return Response(HTTP_409_CONFLICT)
