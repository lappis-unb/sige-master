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
    email = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=30)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            super(CustomUser, self).save(*args, **kwargs)
        except ValidationError as error:
            return error


class ResearcherUser(CustomUser):
    """
    This user type is not capable of accessing the API's slave and transistor
    creation endpoints. Has access to all data inside the master though.
    """
    class Meta:
        # proxy = True
        verbose_name = _('Researcher')


class ManagerUser(CustomUser):
    """
    This user type is capable of accessing all the resources of the master's
    API.
    """
    class Meta:
        # proxy = True
        verbose_name = _('Manager')
