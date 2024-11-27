from typing import Annotated

from pydantic import BaseModel, Field

from .constants import REFERENCE_PK_LENGTH


class DuplicateReference(BaseModel):
    reference_pk: Annotated[str, Field(max_length=REFERENCE_PK_LENGTH)]


class Duplicate(BaseModel):
    first: DuplicateReference
    second: DuplicateReference
    score: Annotated[float, Field(ge=0, le=1, description="Similarity score must be between 0 and 1")]
