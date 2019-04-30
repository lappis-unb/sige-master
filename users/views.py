from rest_framework import viewsets
from rest_framework import serializers

from .models import *
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class ResearcherUserViewSet(viewsets.ModelViewSet):
    queryset = ResearcherUser.objects.all()
    serializer_class = ResearcherUserSerializer


class ManagerUserViewSet(viewsets.ModelViewSet):
    queryset = ManagerUser.objects.all()
    serializer_class = ManagerUserSerializer
