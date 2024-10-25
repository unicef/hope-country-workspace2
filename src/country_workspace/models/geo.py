from django.db import models

from mptt.models import MPTTModel


class Country(models.Model):
    remote_id = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)


class AreaType(MPTTModel):
    remote_id = models.CharField(unique=True, max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Area(MPTTModel):
    remote_id = models.CharField(unique=True, max_length=255)
    type = models.ForeignKey(AreaType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
