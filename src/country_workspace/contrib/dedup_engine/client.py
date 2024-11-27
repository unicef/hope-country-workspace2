from typing import Type

from requests import Session
from requests.auth import AuthBase
from requests.models import PreparedRequest

from country_workspace.contrib.dedup_engine.adapters import (
    DeduplicationSetAdapter,
    DuplicateAdapter,
    IgnoredAdapter,
    ImageAdapter,
)
from country_workspace.contrib.dedup_engine.endpoints import Endpoint
from country_workspace.contrib.dedup_engine.models import (
    DeduplicationSet,
    DeduplicationSetCreate,
    Duplicate,
    Ignored,
    IgnoredCreate,
    Image,
    ImageCreate,
)
from country_workspace.contrib.dedup_engine.types import TCreate, TModel


class Auth(AuthBase):
    def __init__(self, token: str) -> None:
        self._auth_header = f"Token {token}"

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = self._auth_header
        return request


class HDEAPIClient:
    def __init__(self, *, base_url: str, token: str) -> None:
        self.session = Session()
        self.session.auth = Auth(token)
        self.endpoints = Endpoint(base=base_url.rstrip("/"))

    def _get_adapter(
        self, adapter_class: type, model_class: Type[TModel], create_class: Type[TCreate] = None, **kwargs
    ):
        return adapter_class(self.session, self.endpoints, model_class, create_class, **kwargs)

    @property
    def deduplication_set(self) -> DeduplicationSetAdapter:
        return self._get_adapter(DeduplicationSetAdapter, DeduplicationSet, DeduplicationSetCreate)

    @property
    def duplicate(self) -> DuplicateAdapter:
        return self._get_adapter(DuplicateAdapter, Duplicate)

    @property
    def ignored_filenames(self) -> IgnoredAdapter:
        return self._get_adapter(IgnoredAdapter, Ignored, IgnoredCreate, resource_type="filenames")

    @property
    def ignored_reference_pks(self) -> IgnoredAdapter:
        return self._get_adapter(IgnoredAdapter, Ignored, IgnoredCreate, resource_type="reference_pks")

    @property
    def image(self) -> ImageAdapter:
        return self._get_adapter(ImageAdapter, Image, ImageCreate)
