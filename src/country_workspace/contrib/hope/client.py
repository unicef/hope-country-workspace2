import hashlib
import re
import time
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Generator, Optional, Union

import requests
from constance import config
from requests.exceptions import RequestException

from country_workspace.exceptions import RemoteError

from .signals import hope_request_end, hope_request_start

if TYPE_CHECKING:
    JsonType = Union[None, int, str, bool, list["JsonType"], dict[str, "JsonType"]]
    FlatJsonType = dict[str, Union[str, int, bool]]


def sanitize_url(url: str) -> str:
    return re.sub(r"([^:]/)(/)+", r"\1", url)


class HopeClient:

    def __init__(self, token: Optional[str] = None):
        self.token = token or config.HOPE_API_TOKEN

    def get_url(self, path: str) -> str:
        url = sanitize_url("/".join([config.HOPE_API_URL, path]))
        if not url.endswith("/"):
            url = url + "/"
        return url

    def get_lookup(self, path: str) -> "FlatJsonType":
        url = self.get_url(path)
        ret = requests.get(url, headers={"Authorization": f"Token {self.token}"})  # nosec
        if ret.status_code != 200:
            raise RemoteError(f"Error {ret.status_code} fetching {url}")
        return ret.json()

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> "Generator[FlatJsonType, None, None]":
        url: "str|None" = self.get_url(path)
        signature = hashlib.sha256(f"{url}{params}{time.perf_counter_ns()}".encode("utf-8")).hexdigest()
        pages = 0
        hope_request_start.send(self.__class__, url=url, params=params, signature=signature)
        while True:
            if not url:
                break
            try:
                ret = requests.get(
                    url, params=params, headers={"Authorization": f"Token {self.token}"}, timeout=10
                )  # nosec
                if ret.status_code != 200:
                    raise RemoteError(f"Error {ret.status_code} fetching {url}")
                pages += 1
            except RequestException:
                raise RemoteError(f"Remote Error fetching {url}")

            try:
                data = ret.json()
            except JSONDecodeError:
                raise RemoteError(f"Wrong JSON response fetching {url}")
            try:
                for record in data["results"]:
                    yield record
                if "next" in data:
                    url = data["next"]
                else:
                    url = None
            except TypeError:
                raise RemoteError(f"Malformed JSON fetching {url}")
        hope_request_end.send(self.__class__, url=url, params=params, pages=pages, signature=signature)
