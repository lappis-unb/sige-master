from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from users import models


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = models.CustomUser
        fields = ('email', 'username', 'name', 'user_type')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = models.CustomUser
        fields = UserChangeForm.Meta.fields
