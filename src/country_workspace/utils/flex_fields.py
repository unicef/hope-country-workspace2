from hope_flex_fields.models import DataChecker


def get_checker_fields(checker: DataChecker) -> tuple[str, str]:
    for fs in checker.members.select_related("fieldset").all():
        for field in fs.fieldset.get_fields():
            yield field.name, field.attrs.get("label", field.name)
