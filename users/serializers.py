from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'password')

    def create(self, validated_data):
        user = CustomUser(
            name=validated_data.get('name', None),
            email=validated_data.get('email', None),
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
