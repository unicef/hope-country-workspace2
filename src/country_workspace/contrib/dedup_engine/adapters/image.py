from __future__ import annotations

from typing import override
from uuid import UUID

from country_workspace.contrib.dedup_engine.adapters.base import BaseAdapter, HTTPMethod
from country_workspace.contrib.dedup_engine.models import DeduplicationSet, Image, ImageCreate


class ImageAdapter(BaseAdapter[Image, ImageCreate]):

    @override
    def list(self, deduplication_set: DeduplicationSet | UUID) -> list[Image]:
        return super().list(
            url_path=self.endpoints.image,
            deduplication_set_id=self.get_entity_id(deduplication_set),
        )

    @override
    def create(self, deduplication_set: DeduplicationSet | UUID, data: ImageCreate) -> Image:
        return super().create(
            url_path=self.endpoints.image,
            deduplication_set_id=self.get_entity_id(deduplication_set),
            data=data,
        )

    @override
    def destroy(self, deduplication_set: DeduplicationSet | UUID, image: Image | UUID) -> None:
        return super().destroy(
            url_path=self.endpoints.image_detail,
            deduplication_set_id=self.get_entity_id(deduplication_set),
            image_id=self.get_entity_id(image),
        )

    def create_bulk(self, deduplication_set: DeduplicationSet | UUID, data: list[ImageCreate]) -> list[Image]:
        validated_data = [self.validate_data(item, ImageCreate).model_dump(by_alias=True) for item in data]
        response_data = self._action(
            HTTPMethod.POST,
            self.endpoints.image_bulk,
            path_params={"deduplication_set_id": self.get_entity_id(deduplication_set)},
            data=validated_data,
        )
        return [Image(**item) for item in response_data]

    def destroy_bulk(self, deduplication_set: DeduplicationSet | UUID) -> None:
        self._action(
            HTTPMethod.DELETE,
            self.endpoints.image_bulk_clear,
            path_params={"deduplication_set_id": self.get_entity_id(deduplication_set)},
        )

    def retrieve(self, *args, **kwargs) -> None:
        raise NotImplementedError("Retrieval of Image objects is not supported.")
