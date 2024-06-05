from django.db import models

from apps.organizations.models import Entity


class Line(models.Model):
    start_lat = models.FloatField(null=False, blank=False)
    start_lng = models.FloatField(null=False, blank=False)
    end_lat = models.FloatField(null=False, blank=False)
    end_lng = models.FloatField(null=False, blank=False)
    institution = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
