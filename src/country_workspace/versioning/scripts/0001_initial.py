# Generated by Django 5.1.1 on 2024-10-09 06:19
from hope_flex_fields.models import DataChecker, FieldDefinition, Fieldset

from country_workspace.constants import HOUSEHOLD_CHECKER_NAME, INDIVIDUAL_CHECKER_NAME
from country_workspace.versioning.checkers import create_hope_core_fieldset, create_hope_field_definitions


def removes_hope_field_definitions():
    FieldDefinition.objects.filter(name__startswith="HOPE ").delete()


def removes_hope_core_fieldset():
    Fieldset.objects.filter(name=INDIVIDUAL_CHECKER_NAME).delete()
    DataChecker.objects.filter(name=INDIVIDUAL_CHECKER_NAME).delete()

    Fieldset.objects.filter(name=HOUSEHOLD_CHECKER_NAME).delete()
    DataChecker.objects.filter(name=HOUSEHOLD_CHECKER_NAME).delete()


def create_base_fields_definitions():
    from hope_flex_fields.models import FieldDefinition
    from hope_flex_fields.registry import field_registry
    from hope_flex_fields.utils import get_default_attrs, get_kwargs_from_field_class

    for fld in field_registry:
        name = fld.__name__
        from concurrency.utils import fqn

        FieldDefinition.objects.get_or_create(
            name=name,
            field_type=fqn(fld),
            defaults={"attrs": get_kwargs_from_field_class(fld, get_default_attrs())},
        )


def create_default_sys_logs():
    from country_workspace.models import SyncLog

    SyncLog.objects.create_lookups()


class Scripts:
    operations = [
        create_base_fields_definitions,
        (create_hope_field_definitions, removes_hope_field_definitions),
        (create_hope_core_fieldset, removes_hope_core_fieldset),
        create_default_sys_logs,
    ]
