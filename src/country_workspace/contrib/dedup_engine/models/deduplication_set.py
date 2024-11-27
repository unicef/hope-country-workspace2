from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field

from .constants import REFERENCE_PK_LENGTH
from .util import DatetimeEncoderMixin, DeduplicationSetStatus, StatusEncoderMixin, merge_configs


class DeduplicationSetConfig(BaseModel):
    name: Annotated[str | None, Field(max_length=128)] = None
    settings: dict[str, Any] | None = None


class DeduplicationSetCreate(BaseModel):
    reference_pk: Annotated[str, Field(max_length=REFERENCE_PK_LENGTH)]
    name: Annotated[str | None, Field(max_length=128)] = None
    description: str | None = None
    notification_url: Annotated[str | None, Field(max_length=255)] = None


@merge_configs(DatetimeEncoderMixin, StatusEncoderMixin)
class DeduplicationSet(DeduplicationSetCreate):
    id: UUID
    state: DeduplicationSetStatus
    config: DeduplicationSetConfig | None = None
    created_at: datetime
    updated_at: datetime | None = None
    external_system: str
    created_by: int | None = None
    updated_by: int | None = None
