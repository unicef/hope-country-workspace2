from typing import Final

from django.utils import timezone

BATCH_NAME_DEFAULT: Final[str] = f"Batch {timezone.now()}"
