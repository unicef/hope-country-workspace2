import logging
from typing import Any

from django.db.models import Model, QuerySet

logger = logging.getLogger(__name__)


def validate_queryset(queryset: QuerySet[Model], **kwargs: Any) -> dict[str, int]:
    valid = invalid = num = 0
    try:
        for __, entry in enumerate(queryset, 1):
            if entry.validate_with_checker():
                valid += 1
            else:
                invalid += 1
    except Exception as e:
        logger.exception(e)

    return {"valid": valid, "invalid": invalid, "total": num}
