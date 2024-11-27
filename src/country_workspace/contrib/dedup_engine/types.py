from typing import TypeVar

from country_workspace.contrib.dedup_engine.models import (
    DeduplicationSet,
    DeduplicationSetCreate,
    Duplicate,
    Ignored,
    IgnoredCreate,
    Image,
    ImageCreate,
)

TModel = TypeVar(
    "TModel",
    DeduplicationSet,
    Duplicate,
    Ignored,
    Image,
)

TCreate = TypeVar(
    "TCreate",
    DeduplicationSetCreate,
    IgnoredCreate,
    ImageCreate,
)
