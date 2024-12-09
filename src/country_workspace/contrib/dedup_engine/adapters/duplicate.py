from typing import override
from uuid import UUID

from country_workspace.contrib.dedup_engine.adapters.base import BaseAdapter
from country_workspace.contrib.dedup_engine.models import DeduplicationSet, Duplicate


class DuplicateAdapter(BaseAdapter[Duplicate, None]):
    @override
    def list(self, deduplication_set: DeduplicationSet | UUID) -> list[Duplicate]:
        return super().list(
            url_path=self.endpoints.duplicate,
            deduplication_set_id=self.get_entity_id(deduplication_set),
        )

    @override
    def retrieve(self, *args, **kwargs) -> None:
        raise NotImplementedError("Retrieval of Duplicate objects is not supported.")

    @override
    def create(self, *args, **kwargs) -> None:
        raise NotImplementedError("Creation of Duplicate objects is not supported.")

    @override
    def destroy(self, *args, **kwargs) -> None:
        raise NotImplementedError("Deletion of Duplicate objects is not supported.")
