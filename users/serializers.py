from rest_framework import serializers

from .models import CustomUser


class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "name", "password", "user_type")

    def create(self, validated_data):
        user = CustomUser(
            name=validated_data.get("name", None),
            email=validated_data.get("email", None),
            user_type=validated_data.get("user_type", None),
        )
        user.set_password(validated_data.get("password", None))
        user.save()
        return user

    def update(self, instance, validated_data):
        for field in validated_data:
            if field == "password":
                instance.set_password(validated_data.get(field))
            else:
                instance.__setattr__(field, validated_data.get(field))
        instance.save()
        return instance
