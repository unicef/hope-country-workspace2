from django.contrib.auth.models import Group
from django.db import models

from .office import CountryOffice
from .program import Program
from .user import User


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, blank=True, null=True
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    expires = models.DateField(blank=True, null=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_role",
                fields=["user", "country_office", "group"],
            ),
        )
