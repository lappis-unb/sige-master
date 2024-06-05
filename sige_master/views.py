from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import CreateAccountSerializer


class HealthCheck(APIView):
    """
    Returns a "200 OK" response if the server is running normally.
    This endpoint is used for health checks.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "200 OK"}, status=status.HTTP_200_OK)


health_check = HealthCheck.as_view()


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if email is None or password is None:
        return Response({"error": "Please provide email and password"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)

    if not user:
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    serialized_user = CreateAccountSerializer(user)

    return Response({"token": token.key, "user": serialized_user.data}, status=status.HTTP_200_OK)
