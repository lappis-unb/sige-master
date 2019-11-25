from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users import forms
from users import models


class CustomUserAdmin(UserAdmin):
    add_form = forms.CustomUserCreationForm
    form = forms.CustomUserChangeForm
    model = models.CustomUser
    list_display = ['email', 'username']


admin.site.register(models.CustomUser, CustomUserAdmin)
