from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenVerifySerializer,
)

from apps.accounts.models import Account
from apps.accounts.permissions import CustomUserPermissions
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    CreateAccountSerializer,
    DecodePayloadSerializer,
    ListAccountSerializer,
    LoginSerializer,
)


class AccountViewSet(ModelViewSet):
    permission_classes = [CustomUserPermissions, ]
    serializer_class = CreateAccountSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Account.objects.none()
        elif user.is_staff:
            return Account.objects.all()
        elif user.is_admin:
            return Account.objects.filter(organization=user.organization)
        return Account.objects.filter(id=user.id)

    def get_serializer_class(self):
        serializer_map = {
            "create": CreateAccountSerializer,
            "list": ListAccountSerializer,
            "retrieve": ListAccountSerializer,
            "login": TokenObtainPairSerializer,
            "decode_payload": DecodePayloadSerializer,
            "change_password": ChangePasswordSerializer,
            "verify_token": TokenVerifySerializer,
        }
        return serializer_map.get(self.action, super().get_serializer_class())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        account = self.request.user
        if account.is_staff:
            serializer.save(is_approved=True)
        elif account.is_anonymous or account.is_member:
            serializer.save(role=Account.Role.GUEST, is_approved=False)
        elif account.is_admin:
            serializer.save(organization=self.request.user.organization, is_approved=True)
        else:
            raise PermissionDenied("You do not have permission to create an account.")

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token_data = serializer.validated_data["tokens"]

        if settings.SESSION_LOGIN:
            login(request, user)
        return Response(token_data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        if settings.SESSION_LOGIN:
            logout(request)
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="change-password", permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = ListAccountSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="verify-token", permission_classes=[IsAuthenticated])
    def verify_token(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Token is valid"}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="payload", permission_classes=[AllowAny])
    def decode_payload(self, request):
        serializer = DecodePayloadSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({"detail": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
