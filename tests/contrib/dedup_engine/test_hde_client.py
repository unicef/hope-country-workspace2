import pytest
from requests import PreparedRequest

from country_workspace.contrib.dedup_engine.client import (
    Auth,
    DeduplicationSetAdapter,
    DuplicateAdapter,
    HDEAPIClient,
    IgnoredAdapter,
    ImageAdapter,
)
from country_workspace.contrib.dedup_engine.models import (
    DeduplicationSet,
    DeduplicationSetCreate,
    Duplicate,
    Ignored,
    IgnoredCreate,
    Image,
    ImageCreate,
)


def test_auth_header(mock_token):
    auth = Auth(mock_token)
    mock_request = PreparedRequest()
    mock_request.headers = {}
    auth(mock_request)

    assert mock_request.headers["Authorization"] == f"Token {mock_token}"


def test_client_initialization(mock_base_url, mock_token):
    client = HDEAPIClient(base_url=mock_base_url, token=mock_token)

    assert client.session is not None
    assert client.session.auth._auth_header == f"Token {mock_token}"
    assert client.endpoints.base == mock_base_url


@pytest.mark.parametrize(
    "property_name, expected_adapter_class, expected_model_class, expected_create_class, additional_args",
    [
        ("deduplication_set", DeduplicationSetAdapter, DeduplicationSet, DeduplicationSetCreate, {}),
        ("duplicate", DuplicateAdapter, Duplicate, None, {}),
        ("ignored_filenames", IgnoredAdapter, Ignored, IgnoredCreate, {"resource_type": "filenames"}),
        ("ignored_reference_pks", IgnoredAdapter, Ignored, IgnoredCreate, {"resource_type": "reference_pks"}),
        ("image", ImageAdapter, Image, ImageCreate, {}),
    ],
)
def test_client_properties(
    mock_base_url,
    mock_token,
    property_name,
    expected_adapter_class,
    expected_model_class,
    expected_create_class,
    additional_args,
):
    client = HDEAPIClient(base_url=mock_base_url, token=mock_token)
    adapter = getattr(client, property_name)

    assert isinstance(adapter, expected_adapter_class)
    assert adapter.model_class == expected_model_class

    if expected_create_class:
        assert adapter.create_class == expected_create_class

    for key, value in additional_args.items():
        assert getattr(adapter, key) == value
