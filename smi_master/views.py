from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from users.serializers import UserSerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide email and password'},
                        status=HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)

    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)

    serialized_user = UserSerializer(user)

    return Response(
        {'token': token.key, 'user': serialized_user.data},
        status=HTTP_200_OK
    )
