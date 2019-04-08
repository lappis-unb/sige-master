from django.db import models

class Building(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=11)
    acronym = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name
