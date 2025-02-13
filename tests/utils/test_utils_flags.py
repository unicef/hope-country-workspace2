import os
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from country_workspace.state import state
from country_workspace.utils.flags import debug, env_var, header_key, hostname, superuser, validate_bool

if TYPE_CHECKING:
    from django.test.client import RequestFactory


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("LOGGING_LEVEL=CRITICAL", True),
        ("LOGGING_LEVEL=WARN", False),
        ("LOGGING_LEVEL", True),
        ("ERROR", False),
    ],
)
def test_env_var(value: str, result: str) -> None:
    with mock.patch.dict(os.environ, {"LOGGING_LEVEL": "CRITICAL"}, clear=True):
        assert env_var(value) == result


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("CUSTOM_KEY=123", True),
        ("CUSTOM_KEY", True),
        ("CUSTOM_KEY=234", False),
        ("MISSING=222", False),
        ("MISSING", False),
        ("ERROR=[", False),
    ],
)
def test_header_key(rf: "RequestFactory", value: str, result: str) -> None:
    request = rf.get("/", HTTP_CUSTOM_KEY="123")
    with state.configure(request=request):
        assert header_key(value) == result


@pytest.mark.parametrize(("value", "result"), [("localhost", True)])
def test_hostname(rf: "RequestFactory", value: str, result: str) -> None:
    request = rf.get("/", HTTP_HOST=value)
    with state.configure(request=request):
        assert hostname(value, request=request)


def test_debug(rf: "RequestFactory") -> None:
    assert debug(False)


def test_superuser(rf: "RequestFactory", user, admin_user) -> None:
    request = rf.get("/")
    request.user = admin_user
    assert superuser("t", request)


def test_validate_bool():
    assert validate_bool(1)
    assert not validate_bool(0)
    with pytest.raises(ValidationError):
        validate_bool("-")
