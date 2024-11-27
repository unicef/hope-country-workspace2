from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from .constants import REFERENCE_PK_LENGTH


class IgnoredCreate(BaseModel):
    first: Annotated[str, Field(max_length=REFERENCE_PK_LENGTH)]
    second: Annotated[str, Field(max_length=REFERENCE_PK_LENGTH)]


class Ignored(IgnoredCreate):
    id: int
    deduplication_set: UUID
