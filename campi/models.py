from django.db import models


# Create your models here.
class Campus(models.Model):
    name = models.CharField(max_length=50)
    acronym = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    website_addres = models.CharField(max_length=50)

    def __str__():
        return self.name
