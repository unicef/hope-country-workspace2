from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from country_workspace.models import Household
from country_workspace.validators.base import BeneficiaryGroupValidator


class FullHouseholdValidator(BeneficiaryGroupValidator):

    def validate(self, hh: "Household") -> list:
        errs = []
        try:
            hh.heads().get()
        except ObjectDoesNotExist:
            errs.append("This Household does not have Head")
        except MultipleObjectsReturned:
            errs.append("This Household has multiple heads")

        try:
            hh.collectors_primary().get()
        except ObjectDoesNotExist:
            errs.append("This Household does not have Primary Collector")
        except MultipleObjectsReturned:
            errs.append("This Household has multiple Primary Collectors")

        try:
            hh.collectors_alternate().get()
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            errs.append("This Household has multiple Alternate Collectors")

        return errs
