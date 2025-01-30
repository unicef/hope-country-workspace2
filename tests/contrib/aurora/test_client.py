from json import JSONDecodeError
from unittest.mock import Mock, patch

import pytest
import requests
from constance.test.unittest import override_config
from django.conf import settings

from country_workspace.contrib.aurora.client import AuroraClient
from country_workspace.exceptions import RemoteError


@pytest.mark.vcr(use_cassette="sync_aurora_4pages.yaml")
def tests_aurora_client_successfully(mock_aurora_data):
    aurora_client = AuroraClient()
    with override_config(AURORA_API_URL=settings.AURORA_API_URL):
        records = list(aurora_client.get("record"))
        assert all(isinstance(record, dict) for record in records)


@pytest.mark.parametrize(
    "response",
    [
        {"status_code": 404, "json": dict},
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
