from typing import TYPE_CHECKING

from django.template import Context, Library

if TYPE_CHECKING:
    from hope_flex_fields.models import FlexField


register = Library()


@register.simple_tag(takes_context=True)
def field_error(context: Context, field: "FlexField"):
    return context["original"].errors.get(field.name, None)
