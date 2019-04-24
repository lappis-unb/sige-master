from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser


# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
class CustomUser(AbstractBaseUser):
    """
    Custom user abstract model
    """
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=30)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.username

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
    pass


class ManagerUser(CustomUser):
    """
    This user type is capable of accessing all the resources of the master's
    API.
    """
    pass
