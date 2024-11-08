from django.contrib.postgres.fields import ArrayField
from django.db import models

from .base import BaseModel
from .program import Program


class Rdi(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    hhs = ArrayField(models.IntegerField(), help_text="List of HH primary key for this RDI")
    inds = ArrayField(models.IntegerField(), help_text="List of IND primary key for this RDI. Empty if HH is set")

    class Meta:
        verbose_name_plural = "Rdi"
        ordering = ("name",)
