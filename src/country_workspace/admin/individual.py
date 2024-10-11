from django.contrib import admin

from adminfilters.autocomplete import LinkedAutoCompleteFilter

from ..models import Individual
from .base import BaseModelAdmin


@admin.register(Individual)
class IndividualAdmin(BaseModelAdmin):
    list_display = ("name", "country_office")
    readonly_fields = ("country_office",)
    search_fields = ("name",)
    list_filter = (
        ("country_office", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="country_office")),
    )
