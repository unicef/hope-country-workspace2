from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from country_workspace.models.base import Validable


def calculate_checksum_impl(queryset: "QuerySet[Validable]"):
    for record in queryset.all():
        record.save()
