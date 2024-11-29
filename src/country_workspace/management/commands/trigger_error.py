import logging
from typing import Any

from django.core.management import BaseCommand

import sentry_sdk

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> None:  # noqa
        try:
            1 / 0
        except Exception as e:  # pragma: no cover
            sentry_sdk.capture_exception(e)
