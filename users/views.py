from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone

from django_rest_passwordreset.signals import reset_password_token_created
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django_rest_passwordreset.models import ResetPasswordToken

from datetime import timedelta

from .serializers import *
from .models import CustomUser


class CurrentUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        userid = request.path.split('/')
        userid = userid[2]
        try:
            userid = int(userid)
        except Exception:
            return False
        return request.user == CustomUser.objects.get(id=userid)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser | CurrentUserOnly]


class PasswordTokenVerificationView(APIView):

    serializer_class = CustomTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        # get token validation time
        password_reset_token_validation_time = \
            get_password_reset_token_expiry_time()

        # find token
        reset_password_token = ResetPasswordToken \
                                .objects \
                                .filter(key=token) \
                                .first()

        if reset_password_token is None:
            return Response({'status': 'invalid'}, status=HTTP_404_NOT_FOUND)

        # check expiry date
        expiry_date = reset_password_token.created_at + \
            timedelta(hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            # delete expired token
            reset_password_token.delete()
            return Response({'status': 'expired'}, status=HTTP_404_NOT_FOUND)

        # check if user has password to change
        if not reset_password_token.user.has_usable_password():
            return Response({'status': 'irrelevant'})

        return Response({'status': 'OK'})

@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):

    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': 
            f"{settings.FRONT_URL}/reset_password/{reset_password_token.key}" +
            f"?email={reset_password_token.user.email}",
        'site_name': 'SIGE',
        'site_domain': settings.FRONT_URL
    }

    # render email text
    email_html_message = \
        render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = \
        render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {}".format(settings.FRONT_URL),
        # message:
        email_plaintext_message,
        # from:
        "unb.smi@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()