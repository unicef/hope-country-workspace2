from django.db import models

from .base import BaseModel


class Office(BaseModel):
    HQ = "HQ"

    hope_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    long_name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    code = models.CharField(max_length=100, blank=True, null=True, db_index=True, unique=True)
    slug = models.SlugField(max_length=100, blank=True, null=True, db_index=True, unique=True)
    active = models.BooleanField(default=False)

    extra_fields = models.JSONField(default=dict, blank=True, null=False)

    def __str__(self) -> str:
        return str(self.name)
