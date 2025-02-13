from typing import TYPE_CHECKING, Generator
from unittest import mock

import pytest

from country_workspace.state import state
from country_workspace.utils.http import absolute_reverse, absolute_uri, get_client_ip, get_server_host, get_server_url

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.test.client import RequestFactory
    from pytest_django.fixtures import SettingsWrapper


@pytest.fixture(autouse=True)
def r(monkeypatch: "pytest.MonkeyPatch", rf: "RequestFactory") -> Generator[None, None, None]:
    req: "HttpRequest" = rf.get("/", HTTP_HOST="127.0.0.1")
    m = mock.patch("country_workspace.state.state.request", req)
    m.start()
    yield
    m.stop()


def test_absolute_reverse() -> None:
    assert absolute_reverse("admin:index") == "http://127.0.0.1/admin/"


def test_absolute_uri(settings: "SettingsWrapper") -> None:
    assert absolute_uri("aa") == "http://127.0.0.1/aa"
    assert absolute_uri("") == "http://127.0.0.1/"
    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    assert absolute_uri("") == "https://127.0.0.1/"
    with state.configure(request=None):
        assert absolute_uri("") == ""
    with state.configure(request=None):
        assert absolute_uri("/test/") == "/test/"


def test_get_server_host() -> None:
    assert get_server_host() == "127.0.0.1"


def test_get_server_url(settings: "SettingsWrapper") -> None:
    assert get_server_url() == "http://127.0.0.1"
    with state.configure(request=None):
        assert get_server_url() == ""

    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    assert get_server_url() == "https://127.0.0.1"


@pytest.mark.parametrize("key", ["HTTP_X_FORWARDED_FOR", "HTTP_X_REAL_IP", "REMOTE_ADDR"])
def test_get_client_ip(rf: "RequestFactory", key: str) -> None:
    req = rf.get("/", **{key: "1.1.1.1   "})  # type: ignore
    with state.configure(request=req):
        assert get_client_ip() == "1.1.1.1"
