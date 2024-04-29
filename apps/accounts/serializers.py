import contextlib
from datetime import datetime

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError

from apps.accounts.mixins import DynamicFieldsMixin
from apps.accounts.models import Account
from apps.accounts.utils import create_custom_jwt_token


class CreateAccountSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Account
        fields = [
            "id",
            "email",
            "password",
            "confirm_password",
            "role",
            "organization",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "organization": {"required": False},
            "role": {"required": False},
        }

    def validate_role(self, value):
        user = self.context["request"].user
        if not user.is_admin and not user.is_superuser and value is not None:
            raise serializers.ValidationError("Only admins can set the role")

    def validate_organization(self, value):
        user = self.context["request"].user
        if not user.is_admin and not user.is_superuser and value is not None:
            raise serializers.ValidationError("Only admins can set the organization")

    def validate(self, attrs):
        email = attrs.get("email")
        if Account.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists"})

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Password fields didn't match"})

        attrs.pop("confirm_password")
        return attrs

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)

    def to_representation(self, instance):
        tokens = create_custom_jwt_token(instance)
        response = super(CreateAccountSerializer, self).to_representation(instance)
        response["access"] = tokens["access"]
        response["refresh"] = tokens["refresh"]
        return response


class ListAccountSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source="organization.name", allow_null=True, default="")
    role = serializers.CharField(source="get_role_display")

    class Meta:
        model = Account
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "organization",
            "role",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Must include 'email' and 'password'")

        user = authenticate(request=self.context.get("request"), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid provided credentials")

        tokens = create_custom_jwt_token(user)
        attrs["user"] = user
        attrs["tokens"] = tokens
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"new_password": "Password fields didn't match"})
        return attrs


class DecodePayloadSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        token = attrs.get("token")

        with contextlib.suppress(TokenError):
            payload = RefreshToken(token).payload
        with contextlib.suppress(TokenError):
            payload = AccessToken(token).payload

        if not payload:
            raise serializers.ValidationError("Invalid token provided")

        attrs["expires_in"] = datetime.fromtimestamp(payload["exp"]).isoformat()
        attrs["payload"] = payload
        return attrs
