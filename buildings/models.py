from django.db import models

class Building(models.Model):
    phone = models.CharField(max_length=11)
    name = models.CharField(max_length=120, unique=True)
    acronym = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Building, self).save(*args, **kwargs)
