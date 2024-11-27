from typing import Type, override
from uuid import UUID

from requests import Session

from country_workspace.contrib.dedup_engine.adapters.base import BaseAdapter, Endpoint
from country_workspace.contrib.dedup_engine.models import DeduplicationSet, Ignored, IgnoredCreate


class IgnoredAdapter(BaseAdapter[Ignored, IgnoredCreate]):
    def __init__(
        self,
        session: Session,
        endpoints: Endpoint,
        model_class: Type[Ignored],
        create_class: Type[IgnoredCreate],
        resource_type: str,
    ) -> None:
        super().__init__(session, endpoints, model_class, create_class)
        self.resource_type = resource_type

    @override
    def list(self, deduplication_set: DeduplicationSet | UUID) -> list[Ignored]:
        return super().list(
            url_path=self.endpoints.ignored,
            deduplication_set_id=self.get_entity_id(deduplication_set),
            resource_type=self.resource_type,
        )

    @override
    def create(self, deduplication_set: DeduplicationSet | UUID, data: IgnoredCreate) -> Ignored:
        return super().create(
            url_path=self.endpoints.ignored,
            deduplication_set_id=self.get_entity_id(deduplication_set),
            resource_type=self.resource_type,
            data=data,
        )

    @override
    def retrieve(self, *args, **kwargs) -> None:
        raise NotImplementedError("Retrieval of Ignored objects is not supported.")

    @override
    def destroy(self, *args, **kwargs) -> None:
        raise NotImplementedError("Deletion of Ignored objects is not supported.")
