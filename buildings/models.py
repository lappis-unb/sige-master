from django.db import models
from django.core.exceptions import ValidationError

from utils import phone_validator
from campi.models import Campus


class Building(models.Model):
    
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_validator],
        default=""
    )
    name = models.CharField(max_length=120)
    acronym = models.CharField(max_length=30)
  
    class Meta:
        unique_together = (("campus", "name"), ("campus", "acronym"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Building, self).save(*args, **kwargs)
