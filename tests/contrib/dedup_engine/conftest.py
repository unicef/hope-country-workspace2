import pytest
from pytest_mock import MockFixture

from country_workspace.contrib.dedup_engine.client import HDEAPIClient


@pytest.fixture
def mock_base_url():
    return "https://example.com"


@pytest.fixture
def mock_token():
    return "test_token"


@pytest.fixture
def mock_hde_client(mocker: MockFixture, mock_base_url, mock_token) -> HDEAPIClient:
    return HDEAPIClient(base_url=mock_base_url, token=mock_token)
