from django.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    number = models.CharField(max_length=10, verbose_name=_('Number'), blank=True)
    complement = models.CharField(max_length=255, blank=True, verbose_name=_('Complement'))
    zip_code = models.CharField(max_length=20, verbose_name=_('CEP'))
    city = models.ForeignKey('City', on_delete=models.PROTECT, verbose_name=_('City'))

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return f'{self.address}, {self.number}, {self.city} - {self.city.state.name}'


class State(models.Model):
    code = models.PositiveSmallIntegerField(verbose_name=_('IBGE Code'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    acronym = models.CharField(max_length=2, verbose_name=_('Acronym'))

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        return f'{self.code} - {self.name}/{self.acronym}'


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        verbose_name=_('State'),
        related_name='cities'
    )

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return f'{self.name}'


class GeographicLocation(models.Model):
    class MapType(models.IntegerChoices):
        ROADMAP = 1, _('Roadmap')
        SATELLITE = 2, _('Satellite')
        HYBRID = 3, _('Hybrid')
        TERRAIN = 4, _('Terrain')

    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Latitude'))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Longitude'))
    zoom_level = models.PositiveSmallIntegerField(default=16, verbose_name=_('Zoom Level'))
    tilt = models.PositiveSmallIntegerField(default=0, verbose_name=_('Tilt'))
    map_type = models.PositiveSmallIntegerField(
        choices=MapType.choices,
        default=MapType.ROADMAP,
        verbose_name=_('Map Type')
    )

    class Meta:
        verbose_name = _('Geographic Location')
        verbose_name_plural = _('Geographic Locations')

    def __str__(self):
        return f'{self.latitude}, {self.longitude}'
