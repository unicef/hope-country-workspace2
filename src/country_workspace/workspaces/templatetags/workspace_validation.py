from typing import TYPE_CHECKING

from django.template import Context, Library

if TYPE_CHECKING:
    from django.forms import BoundField

    from country_workspace.models.base import Validable


register = Library()


@register.simple_tag(takes_context=True)
def field_error(context: Context, field: "BoundField"):
    obj: "Validable" = context["original"]
    form_errors = field.form.errors.get(field.name, [])
    errs = obj.errors.get(field.name, [])
    return form_errors + errs
