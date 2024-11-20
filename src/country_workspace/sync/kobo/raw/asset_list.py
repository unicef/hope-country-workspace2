from typing import TypedDict

from country_workspace.sync.kobo.raw.common import ListResponse


class Asset(TypedDict):
    data: str
    url: str


class AssetList(ListResponse):
    results: list[Asset]
