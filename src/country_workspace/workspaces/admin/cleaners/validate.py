import logging

logger = logging.getLogger(__name__)


def validate_queryset(queryset, **kwargs) -> dict[str, int]:
    valid = invalid = num = 0
    try:
        for num, entry in enumerate(queryset, 1):
            if entry.validate_with_checker():
                valid += 1
            else:
                invalid += 1
    except Exception as e:
        logger.exception(e)

    return {"valid": valid, "invalid": invalid, "total": num}
