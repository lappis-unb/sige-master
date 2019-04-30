from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import *
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ResearcherUser)
admin.site.register(ManagerUser)
