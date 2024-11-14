from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Household, Individual, Program
from ..workspaces.models import CountryHousehold, CountryIndividual, CountryProgram
from .manager import cache_manager


@receiver(post_save)
def update_cache(sender, instance, **kwargs):
    if isinstance(instance, (Household, Individual, CountryHousehold, CountryIndividual)):
        program = instance.program
        cache_manager.incr_cache_version(program=program)
    elif isinstance(instance, (Program, CountryProgram)):
        program = instance
        cache_manager.incr_cache_version(program=program)
