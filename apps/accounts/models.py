from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager
from apps.organizations.models import Organization


class Account(AbstractUser):
    class Role(models.IntegerChoices):
        MANAGER = 1, _("Manager")
        ADMIN = 2, _("Admin")
        OPERATOR = 3, _("Operator")
        GUEST = 4, _("Guest")

    username = None
    base_role = Role.GUEST
    email = models.EmailField(_("email address"), unique=True)
    role = models.IntegerField(choices=Role.choices)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.pk:
            if not (self.is_superuser or self.is_admin):
                self.role = self.base_role
        return super().save(*args, **kwargs)

    @property
    def is_manager(self):
        return self.role == Account.Role.MANAGER

    @property
    def is_admin(self):
        return self.role == Account.Role.ADMIN

    @property
    def is_operator(self):
        return self.role == Account.Role.OPERATOR

    @property
    def is_guest(self):
        return self.role == Account.Role.GUEST
