from django.db import models


# Create your models here.
class Campus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    acronym = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50, unique=True)
    website_address = models.CharField(max_length=50)

    def __str__(self):
        return self.name
