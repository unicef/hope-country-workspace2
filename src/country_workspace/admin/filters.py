from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext as _


class FailedFilter(SimpleListFilter):
    title = "Status"
    parameter_name = "failed"

    def lookups(self, request, model_admin):
        return (
            ("f", _("Failed")),
            ("s", _("Success")),
        )

    def get_title(self):
        return self.title

    def queryset(self, request, queryset):
        if self.value() == "s":
            return queryset.filter(sentry_id__isnull=True)
        elif self.value() == "f":
            return queryset.filter(sentry_id__isnull=False)
        return queryset

    def has_output(self):
        return True

    def html_attrs(self):
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
    # template = "workspace/adminfilters/combobox.html"

    def lookups(self, request, model_admin):
        return (
            ("v", _("Valid")),
            ("i", _("Invalid")),
            ("u", _("Not Verified")),
        )

    def get_title(self):
        return self.title

    def queryset(self, request, queryset):
        if self.value() == "v":
            return queryset.filter(last_checked__isnull=False).filter(errors__iexact="{}")
        elif self.value() == "i":
            return queryset.filter(last_checked__isnull=False).exclude(errors__iexact="{}")
        elif self.value() == "u":
            return queryset.filter(last_checked__isnull=True)
        return queryset

    def has_output(self):
        return True

    def html_attrs(self):
        classes = f"adminfilters  {self.__class__.__name__.lower()}"
        if self.value():
            classes += " active"

        return {
            "class": classes,
            "id": "_".join(self.expected_parameters()),
        }
