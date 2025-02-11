import contextlib
from copy import copy
from threading import local
from typing import TYPE_CHECKING

from django.core.signing import get_cookie_signer

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

    from django.http import HttpRequest, HttpResponse

    from .models import Office, Program

not_set = object()


class State(local):
    request: "HttpRequest|None" = None
    tenant_cookie: "str|None" = None
    program_cookie: "str|None" = None
    tenant: "Office|None" = None
    program: "Program|None" = None
    cookies: "dict[str, list[Any]]" = {}
    filters: "list[Any]" = []
    inspecting: bool = False

    def __repr__(self) -> str:
        return f"<State {id(self)}: {self.tenant_cookie}>"

    @contextlib.contextmanager
    def configure(self, **kwargs: "dict[str,Any]") -> "Iterator[None]":
        pre = copy(self.__dict__)
        self.reset()
        with self.set(**kwargs):
            yield
        for k, v in pre.items():
            setattr(self, k, v)

    @contextlib.contextmanager
    def set(self, **kwargs: "dict[str,Any]") -> "Iterator[None]":
        pre = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                pre[k] = getattr(self, k)
            else:
                pre[k] = not_set
            setattr(self, k, v)
        yield
        for k, v in pre.items():
            if v is not_set:
                delattr(self, k)
            else:
                setattr(self, k, v)

    def set_selected_tenant(self, tenant: "Office") -> None:
        from country_workspace.workspaces.config import conf

        self.tenant = tenant
        signer = get_cookie_signer()
        self.add_cookies(conf.TENANT_COOKIE_NAME, signer.sign(tenant.slug))

    def set_selected_program(self, program: "Program") -> None:
        self.program = program
        signer = get_cookie_signer()
        self.add_cookies("selected_program", signer.sign(program.id))

    def add_cookies(  # noqa: PLR0913
        self,
        key: str,
        value: str,
        max_age: "int|None" = None,
        expires: "int|None" = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: "Any" = None,
    ) -> None:
        self.cookies[key] = [
            value,
            max_age,
            expires,
            path,
            domain,
            secure,
            httponly,
            samesite,
        ]

    def set_cookies(self, response: "HttpResponse") -> None:
        for name, args in self.cookies.items():
            response.set_cookie(name, *args)

    def reset(self) -> None:
        self.tenant = None
        self.program = None
        self.tenant_cookie = None
        self.request = None
        self.cookies = {}
        self.filters = []
        self.inspecting = False


state = State()
