from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from rest_framework.status import HTTP_409_CONFLICT
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.dispatch import receiver

from django_rest_passwordreset.signals import reset_password_token_created

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

@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):

    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}/reset_password/{}".format(settings.FRONT_URL, reset_password_token.key),
        'site_name': 'SIGE',
        'site_domain': settings.FRONT_URL
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

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