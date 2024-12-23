from django.template import Library

register = Library()


@register.filter
def is_safe_celery_info(entry: str) -> bool:
    return entry not in [
        "traceback",
        "children",
        "task_args",
        "task_kwargs",
    ]
