from django.db import models
from django.core.exceptions import ValidationError

from utils import web_site_validator
from utils import phone_validator


class Campus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    acronym = models.CharField(max_length=50, unique=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_validator],
        default=""
    )
    address = models.CharField(max_length=50, unique=True)
    website_address = models.CharField(
        max_length=50,
        blank=True,
        validators=[web_site_validator],
        default=""
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Campus, self).save(*args, **kwargs)
