from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
class CustomUser(AbstractUser):
    """
    Custom user abstract model
    """
    USER_TYPES = (
        ('rsc', 'researcher'),
        ('man', 'manager'),
        ('adm', 'admin')
    )

    email = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=30)
    user_type = models.CharField(max_length=3,
        choices=USER_TYPES, default='man')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'user_type']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        try:
            self.is_admin = self.user_type  == 'adm'
            self.is_staff = self.user_type == 'man' or self.user_type == 'rsc'
            self.full_clean()
            super(CustomUser, self).save(*args, **kwargs)
        except ValidationError as error:
            raise error
