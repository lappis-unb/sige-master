from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from utils import web_site_validator
from utils import phone_validator


class Campus(models.Model):

    class Meta:
        # Campi is the plural for the latin word campus
        verbose_name = _('Campus')
        verbose_name_plural = _('Campi')

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Name'),
        help_text=_('This field is required')
    )
    acronym = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Acronym'),
        help_text=_('This field is required')
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Campus, self).save(*args, **kwargs)
