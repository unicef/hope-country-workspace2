from enum import Enum
from typing import Any, Generic, Type

from requests import Session

from country_workspace.contrib.dedup_engine.adapters.mixins import URLMixin, ValidationMixin
from country_workspace.contrib.dedup_engine.endpoints import Endpoint
from country_workspace.contrib.dedup_engine.types import TCreate, TModel


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class BaseAdapter(Generic[TModel, TCreate], URLMixin, ValidationMixin):
    def __init__(
        self, session: Session, endpoints: Endpoint, model_class: Type[TModel], create_class: Type[TCreate] = None
    ) -> None:
        self.session = session
        self.endpoints = endpoints
        self.model_class = model_class
        self.create_class = create_class or model_class

    def list(self, url_path: str, **kwargs) -> list[TModel]:
        url = self.prepare_url(url_path, **kwargs)
        response = self._request(HTTPMethod.GET.value, url)
        return [self.model_class(**item) for item in response.json()]

    def retrieve(self, url_path: str, **kwargs) -> TModel:
        url = self.prepare_url(url_path, **kwargs)
        response = self._request(HTTPMethod.GET.value, url)
        return self.model_class(**response.json())

    def create(self, url_path: str, data: TCreate, **kwargs) -> TModel:
        url = self.prepare_url(url_path, **kwargs)
        response = self._request(
            HTTPMethod.POST.value, url, json=self.validate_data(data, self.create_class).model_dump(by_alias=True)
        )
        print(f"{response.json()=}")
        return self.model_class(**response.json())

    def destroy(self, url_path: str, **kwargs) -> None:
        url = self.prepare_url(url_path, **kwargs)
        response = self._request(HTTPMethod.DELETE.value, url)
        if response.status_code != 204:
            response.raise_for_status()

    def update(self, url_path: str, data: TModel, **kwargs) -> TModel:
        raise NotImplementedError("Update method is not implemented")

    def _request(self, method: str, url: str, **kwargs) -> Any:
        print(f"{method} {url=}")
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def _action(
        self,
        method: HTTPMethod,
        url_path: str,
        *,
        path_params: dict[str, Any] = None,
        data: Any = None,
    ) -> Any:
        path_params = path_params or {}
        url = self.prepare_url(url_path, **path_params)
        response = self._request(method.value, url, json=data)
        if response.content:
            return response.json()
        return None
