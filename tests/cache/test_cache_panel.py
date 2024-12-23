from unittest import mock
from unittest.mock import MagicMock

import pytest

from country_workspace.admin import panel_cache
from country_workspace.cache.manager import CacheManager


@pytest.fixture
def manager(worker_id):
    m = CacheManager(f"cache{worker_id}")
    m.init()
    m.active = True
    return m


def test_cache_panel(rf):
    req = rf.get("/")
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200


def test_cache_panel_invalid(rf):
    req = rf.post("/", {})
    res = panel_cache(MagicMock(each_context=lambda s: {}), req)
    assert res.status_code == 200


def test_cache_panel_filter(rf, manager):
    with mock.patch("country_workspace.cache.smart_panel.cache_manager", manager):
        k = manager.build_key("test_cache_panel_entry")
        manager.store(k, 1)
        req = rf.post("/", {"pattern": "test_cache_panel_entry"})
        res = panel_cache(MagicMock(each_context=lambda s: {}), req)
        assert res.status_code == 200
        assert b"test_cache_panel_entry" in res.content


def test_cache_panel_delete(rf, manager):
    with mock.patch("country_workspace.cache.smart_panel.cache_manager", manager):
        k = manager.build_key("test_cache_panel_delete")
        manager.store(k, 1)
        req = rf.post("/", {"pattern": "*cache_panel_delete*", "_delete": "Delete"})
        res = panel_cache(MagicMock(each_context=lambda s: {}), req)
        assert res.status_code == 302

        req = rf.post("/", {"pattern": "xx", "_delete": "Delete"})
        res = panel_cache(MagicMock(each_context=lambda s: {}), req)
        assert res.status_code == 302


def test_cache_panel_toggle(rf, manager):
    with mock.patch("country_workspace.cache.smart_panel.cache_manager", manager):
        req = rf.post("/", {"pattern": "*", "_disable": "D"})
        res = panel_cache(MagicMock(each_context=lambda s: {}), req)
        assert res.status_code == 302
        assert not manager.active

        req = rf.post("/", {"pattern": "*", "_enable": "E"})
        res = panel_cache(MagicMock(each_context=lambda s: {}), req)
        assert res.status_code == 302
        assert manager.active
