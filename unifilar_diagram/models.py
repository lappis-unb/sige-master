from django.db import models
from campi.models import Campus
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField( null=False, blank=False)
    longitude = models.FloatField( null=False, blank=False)
    campus = models.ForeignKey(Campus, 
        on_delete=models.CASCADE, 
        null=False,
        blank=False)

    def __str__(self):
        return self.name


class TransmissionLine(models.Model):
    origin_station = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='lines_origin')
    destination_station = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='lines_destination')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Line {self.origin_station} -> {self.destination_station}'


class PowerSwitch(models.Model):
    origin_station = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='switches_origin')
    destination_station = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='switches_destination')
    active = models.BooleanField(default=True)
    switched_on = models.BooleanField(default=True)

    def __str__(self):
        return f'Switch {self.origin_station} -> {self.destination_station}'


@receiver(post_save, sender=PowerSwitch)
def update_transmission_lines(sender, instance, **kwargs):
    affected_lines = TransmissionLine.objects.filter(origin_station__gte=instance.origin_station)
    if instance.switched_on:
        affected_lines.update(active=True)
    else:
        posterior_lines = affected_lines.filter(Q(origin_station__gt=instance.origin_station) | Q(destination_station__gt=instance.destination_station))
        posterior_lines.update(active=False)