import os
from typing import Any

from django.http import HttpRequest

from country_workspace import VERSION
from country_workspace.state import state


def current_state(request: HttpRequest) -> dict[str, Any]:
    return {
        "state": state,
        "app": {
            "version": VERSION,
            "build_date": os.environ.get("BUILD_DATE", ""),
            "commit": os.environ.get("GIT_SHA", "-"),
            "branch": os.environ.get("BRANCH", "-"),
        },
    }
