from django.db import models
from campi.models import Campus


class Building(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    phone = models.CharField(max_length=11, blank=True, default="")
    name = models.CharField(max_length=120, unique=True)
    acronym = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Building, self).save(*args, **kwargs)
