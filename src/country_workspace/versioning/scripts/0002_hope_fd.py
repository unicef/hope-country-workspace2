from country_workspace.versioning.hope_fields import create_hope_field_definitions, removes_hope_field_definitions


class Scripts:
    requires = []
    operations = [
        (create_hope_field_definitions, removes_hope_field_definitions),
    ]
