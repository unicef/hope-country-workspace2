# Generated by Django 5.1.1 on 2024-10-09 06:19
from flags.state import enable_flag
from hope_flex_fields.models import DataChecker, Fieldset

from country_workspace.contrib.hope.constants import HOUSEHOLD_CHECKER_NAME, INDIVIDUAL_CHECKER_NAME


def removes_hope_core_fieldset() -> None:
    Fieldset.objects.filter(name=INDIVIDUAL_CHECKER_NAME).delete()
    DataChecker.objects.filter(name=INDIVIDUAL_CHECKER_NAME).delete()

    Fieldset.objects.filter(name=HOUSEHOLD_CHECKER_NAME).delete()
    DataChecker.objects.filter(name=HOUSEHOLD_CHECKER_NAME).delete()


def create_default_fields_definitions() -> None:
    from hope_flex_fields.models import FieldDefinition
    from hope_flex_fields.registry import field_registry
    from hope_flex_fields.utils import get_common_attrs, get_kwargs_from_field_class

    for fld in field_registry:
        name = fld.__name__
        from concurrency.utils import fqn

        FieldDefinition.objects.get_or_create(
            name=name,
            field_type=fqn(fld),
            defaults={"attrs": get_kwargs_from_field_class(fld, get_common_attrs())},
        )


def enable_local_login() -> None:
    enable_flag("LOCAL_LOGIN")


class Scripts:
    requires = []

    operations = [
        enable_local_login,
        create_default_fields_definitions,
    ]
