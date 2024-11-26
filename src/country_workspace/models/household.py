from functools import cached_property
from typing import TYPE_CHECKING

from django.db import models

import reversion

from .base import BaseModel, Validable

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope_flex_fields.models import DataChecker

    from .individual import Individual
    from .office import Office
    from .program import Program


@reversion.register()
class Household(Validable, BaseModel):
    system_fields = models.JSONField(default=dict, blank=True)
    members: "QuerySet[Individual]"

    class Meta:
        verbose_name = "Household"

    @cached_property
    def checker(self) -> "DataChecker":
        return self.program.household_checker

    @cached_property
    def program(self) -> "Program":
        return self.batch.program

    @cached_property
    def country_office(self) -> "Office":
        return self.batch.program.country_office

    def validate_with_checker(self) -> bool:
        super().validate_with_checker()
        errors = self.program.beneficiary_validator.validate(self)
        if errors:
            self.errors["dct"] = errors
        self.save(update_fields=["errors"])
        return not bool(self.errors)

    # Business methods

    def heads(self):
        return self.members.filter(flex_fields__relationship="HEAD")

    def collectors_primary(self):
        return self.members.filter(flex_fields__primary_collector_id=self.flex_fields["household_id"])

    def collectors_alternate(self):
        return self.members.filter(flex_fields__primary_collector_id=self.flex_fields["household_id"])
