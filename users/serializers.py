from rest_framework import serializers
from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('email', 'name', 'username', 'user_type')

    def create(self, validated_data):
        return models.CustomUser.objects.create(**validated_data)


class ResearcherUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ResearcherUser
        fields = ('email', 'name', 'username', 'user_type')


class ManagerUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ManagerUser
        fields = ('email', 'name', 'username', 'user_type')
