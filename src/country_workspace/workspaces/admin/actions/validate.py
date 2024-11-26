import logging

from django.db.models import QuerySet

from country_workspace.config.celery import app

logger = logging.getLogger(__name__)


def validate_queryset(self, queryset: QuerySet) -> dict[str, int]:
    try:
        num = valid = invalid = 0
        for num, entry in enumerate(queryset.all(), 1):
            if entry.validate_with_checker():
                valid += 1
            else:
                invalid += 1
    except Exception as e:
        logger.exception(e)

    return {"valid": valid, "invalid": invalid, "total": num}


@app.task()
def validate_program(program_pk: int, limit_to: list[int] | None = None) -> None:
    pass
