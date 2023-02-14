from django.db import models
from django.utils.translation import gettext_lazy as _


CONTRACT_TYPE_OPTIONS = (
    ('Verde', 'Verde'),
    ('Azul', 'Azul')
)


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
    geolocation_latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('latitude')
    )
    geolocation_longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('longitude')
    )
    zoom_ratio = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        default=16,
        verbose_name=_('map zoom')
    )

    contract_type = models.CharField(
        max_length=10, 
        choices=CONTRACT_TYPE_OPTIONS,
        default="Azul",
        blank=True,
        verbose_name=_('contract type')
    )

    off_peak_demand = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('off peak demand')
    )

    peak_demand = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('peak demand')
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Campus, self).save(*args, **kwargs)


class Tariff(models.Model):
    start_date = models.DateField()
    campus = models.ForeignKey(Campus, models.CASCADE)
    regular_tariff = models.FloatField(max_length=10)
    high_tariff = models.FloatField(max_length=10)

    class Meta:
        unique_together = [['start_date', 'campus']]

    def __str__(self):
        return ('<campus: %s, start_date: %s, regular_tariff %s,'
                'high_tariff: %s') % (self.campus, self.start_date)
