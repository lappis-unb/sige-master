from rest_framework import serializers
from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('email', 'name', 'username')


class ResearcherUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ResearcherUser
        fields = ('email', 'name', 'username')


class ManagerUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ManagerUser
        fields = ('email', 'name', 'username')
