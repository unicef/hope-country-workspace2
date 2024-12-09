from typing import Any, Type
from urllib.parse import urljoin
from uuid import UUID

from country_workspace.contrib.dedup_engine.models import DeduplicationSet, Image
from country_workspace.contrib.dedup_engine.types import TModel


class URLMixin:
    def prepare_url(self, path: str, **kwargs) -> str:
        try:
            formatted_path = path.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing placeholder '{e.args[0]}' in kwargs for path: '{path}'")
        return urljoin(self.endpoints.base, formatted_path)


class ValidationMixin:
    @staticmethod
    def get_entity_id(entity: DeduplicationSet | Image | UUID, id_field: str = "id") -> UUID:
        match entity:
            case UUID():
                return entity
            case _ if isinstance(entity, (DeduplicationSet, Image)):
                try:
                    return getattr(entity, id_field)
                except AttributeError:
                    raise AttributeError(f"'{type(entity).__name__}' does not have '{id_field}' attribute")
            case _:
                raise TypeError(
                    f"Invalid type for entity: {type(entity).__name__}. Expected UUID, DeduplicationSet, or Image."
                )

    @staticmethod
    def validate_data(data: Any, model_class: Type[TModel]) -> TModel:
        match data:
            case model_class():
                return data
            case dict():
                return model_class.model_validate(data)
            case _:
                raise TypeError(
                    f"Expected data to be of type {model_class.__name__} or dict, but got {type(data).__name__}"
                )
