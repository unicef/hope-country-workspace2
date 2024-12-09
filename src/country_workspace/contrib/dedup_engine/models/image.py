from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from .constants import REFERENCE_PK_LENGTH
from .util import DatetimeEncoderMixin, merge_configs


class ImageCreate(BaseModel):
    reference_pk: Annotated[str, Field(max_length=REFERENCE_PK_LENGTH)]
    filename: Annotated[str, Field(max_length=255)]


@merge_configs(DatetimeEncoderMixin)
class Image(ImageCreate):
    id: UUID
    deduplication_set: UUID
    created_by: int | None = None
    created_at: datetime
