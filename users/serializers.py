from rest_framework import serializers
from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = models.CustomUser
        fields = ('id', 'email', 'name', 'username', 'user_type', 'password')

    def create(self, validated_data):
        user = models.CustomUser(
            username=validated_data.get('username', None),
            email=validated_data.get('email', None),
            name=validated_data.get('name', None),
            user_type=validated_data.get('user_type', None),
        )
        user.set_password(validated_data.get('password', None))
        user.save()
        return user

    def update(self, instance, validated_data):
        for field in validated_data:
            if field == 'password':
                instance.set_password(validated_data.get(field))
            else:
                instance.__setattr__(field, validated_data.get(field))
        instance.save()
        return instance
