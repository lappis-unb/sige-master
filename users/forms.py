from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import *


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'username', 'name')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class ResearcherUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = ResearcherUser
        fields = ('email', 'username', 'name')


class ResearcherUserChangeForm(UserChangeForm):

    class Meta:
        model = ResearcherUser
        fields = UserChangeForm.Meta.fields


class ManagerUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = ManagerUser
        fields = ('email', 'username', 'name')


class ManagerUserChangeForm(UserChangeForm):

    class Meta:
        model = ManagerUser
        fields = UserChangeForm.Meta.fields
