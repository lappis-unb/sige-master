from django.db import models
from campi.models import Campus


class Line(models.Model):
    start_lat = models.FloatField(null=False, blank=False)
    start_lng = models.FloatField(null=False, blank=False)
    end_lat = models.FloatField(null=False, blank=False)
    end_lng = models.FloatField(null=False, blank=False)
    campus = models.ForeignKey(
        Campus, 
        on_delete=models.CASCADE, 
        null=False,
        blank=False)
