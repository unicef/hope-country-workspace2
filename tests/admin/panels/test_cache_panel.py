from unittest.mock import MagicMock

from country_workspace.admin import panel_cache
from country_workspace.cache.manager import cache_manager


def test_cache_panel(rf):
    req = rf.get("/")
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200


def test_cache_panel_invalid(rf):
    req = rf.post("/", {})
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200


def test_cache_panel_filter(rf):
    k = cache_manager.build_key("test_cache_panel_entry")
    cache_manager.store(k, 1)
    req = rf.post("/", {"pattern": "test_cache_panel_entry"})
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200
    assert b"test_cache_panel_entry" in res.content


def test_cache_panel_delete(rf):
    k = cache_manager.build_key("test_cache_panel_delete")
    cache_manager.store(k, 1)
    req = rf.post("/", {"pattern": "*cache_panel_delete*", "_delete": "Delete"})
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200

    req = rf.post("/", {"pattern": "xx", "_delete": "Delete"})
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200
