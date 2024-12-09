from typing import override
from uuid import UUID

from country_workspace.contrib.dedup_engine.adapters.base import BaseAdapter, HTTPMethod
from country_workspace.contrib.dedup_engine.models import DeduplicationSet, DeduplicationSetCreate


class DeduplicationSetAdapter(BaseAdapter[DeduplicationSet, DeduplicationSetCreate]):
    @override
    def list(self) -> list[DeduplicationSet]:
        return super().list(url_path=self.endpoints.deduplication_set)

    @override
    def retrieve(self, data: DeduplicationSet | UUID) -> DeduplicationSet:
        return super().retrieve(
            url_path=self.endpoints.deduplication_set_detail,
            deduplication_set_id=self.get_entity_id(data),
        )

    @override
    def create(self, data: DeduplicationSetCreate) -> DeduplicationSet:
        return super().create(
            url_path=self.endpoints.deduplication_set,
            data=data,
        )

    @override
    def destroy(self, data: DeduplicationSet | UUID) -> None:
        super().destroy(
            url_path=self.endpoints.deduplication_set_detail,
            deduplication_set_id=self.get_entity_id(data),
        )

    def process(self, data: DeduplicationSet | UUID) -> None:
        self._action(
            HTTPMethod.POST,
            self.endpoints.process,
            path_params={"deduplication_set_id": self.get_entity_id(data)},
        )
