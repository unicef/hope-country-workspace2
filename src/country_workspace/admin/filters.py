from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.db.models import Model, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _


class FailedFilter(SimpleListFilter):
    title = "Status"
    parameter_name = "failed"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> tuple[tuple[str, str], ...]:
        return (
            ("f", _("Failed")),
            ("s", _("Success")),
        )

    def get_title(self) -> str:
        return self.title

    def queryset(self, request: HttpRequest, queryset: QuerySet[Model]) -> QuerySet[Model]:
        if self.value() == "s":
            return queryset.filter(sentry_id__isnull=True)
        if self.value() == "f":
            return queryset.filter(sentry_id__isnull=False)
        return queryset

    def has_output(self) -> bool:
        return True

    def html_attrs(self) -> dict[str, str]:
        classes = f"adminfilters  {self.__class__.__name__.lower()}"
        if self.value():
            classes += " active"

        return {
            "class": classes,
            "id": "_".join(self.expected_parameters()),
        }


class IsValidFilter(SimpleListFilter):
    title = "Valid"
    parameter_name = "valid"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> tuple[tuple[str, str], ...]:
        return (
            ("v", _("Valid")),
            ("i", _("Invalid")),
            ("u", _("Not Verified")),
        )

    def get_title(self) -> str:
        return self.title

    def queryset(self, request: HttpRequest, queryset: QuerySet[Model]) -> QuerySet[Model]:
        if self.value() == "v":
            return queryset.filter(last_checked__isnull=False).filter(errors__iexact="{}")
        if self.value() == "i":
            return queryset.filter(last_checked__isnull=False).exclude(errors__iexact="{}")
        if self.value() == "u":
            return queryset.filter(last_checked__isnull=True)
        return queryset

    def has_output(self) -> bool:
        return True

    def html_attrs(self) -> dict[str, str]:
        classes = f"adminfilters  {self.__class__.__name__.lower()}"
        if self.value():
            classes += " active"

        return {
            "class": classes,
            "id": "_".join(self.expected_parameters()),
        }
