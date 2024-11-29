from json import JSONDecodeError
from unittest.mock import Mock, patch

from django.conf import settings

import pytest
import requests
from constance.test.unittest import override_config

from country_workspace.contrib.aurora.client import AuroraClient
from country_workspace.exceptions import RemoteError


def tests_aurora_client_successfully(mock_vcr, mock_aurora_data):
    aurora_client = AuroraClient()
    with patch("requests.get", wraps=requests.get) as mock_get:
        with override_config(AURORA_API_URL=settings.AURORA_API_URL):
            with mock_vcr.use_cassette(mock_aurora_data["cassette_name"]):
                records = list(aurora_client.get("record"))
                assert all(isinstance(record, dict) for record in records)
                assert len(records) == mock_aurora_data["pages"] * mock_aurora_data["records_per_page"]
                assert mock_get.call_count == mock_aurora_data["pages"]


@pytest.mark.parametrize(
    "response",
    [
        {"status_code": 404, "json": lambda: {}},
        requests.RequestException(),
        JSONDecodeError("Expecting value", "line 1 column 1 (char 0)", 0),
    ],
)
def test_aurora_client_exceptions(response):
    aurora_client = AuroraClient()
    if isinstance(response, Exception):
        if isinstance(response, JSONDecodeError):
            with patch("requests.get") as mock_get:
                mock_get.return_value = Mock(status_code=200)
                mock_get.return_value.json.side_effect = response
                with pytest.raises(RemoteError):
                    list(aurora_client.get("record"))
        else:
            with patch("requests.get", side_effect=response):
                with pytest.raises(RemoteError):
                    list(aurora_client.get("record"))
    else:
        with patch("requests.get") as mock_get:
            mock_get.return_value = Mock(**response)
            with pytest.raises(RemoteError):
                list(aurora_client.get("record"))
