from typing import Any, Generator
from urllib.parse import urljoin

import requests
from constance import config


class AuroraClient:
    """
    A client for interacting with the Aurora API.

    Provides methods to fetch data from the Aurora API with authentication.
    Handles pagination automatically for large datasets.
    """

    def __init__(self, token: str | None = None) -> None:
        """
        Initialize the AuroraClient.

        Args:
            token (str | None): An optional API token for authentication. If not provided,
                the token is retrieved from the Constance configuration (config.AURORA_API_TOKEN).
        """
        self.token = token or config.AURORA_API_TOKEN

    def _get_url(self, path: str) -> str:
        """
        Construct a fully qualified URL for the Aurora API.

        Args:
            path (str): The relative API path.

        Returns:
            str: The full URL, ensuring it ends with a trailing slash.
        """
        url = urljoin(config.AURORA_API_URL, path)
        if not url.endswith("/"):
            url = url + "/"
        return url

    def get(self, path: str) -> Generator[dict[str, Any], None, None]:
        """
        Fetch records from the Aurora API with automatic pagination.

        Args:
            path (str): The relative API path to fetch data from.

        Yields:
            dict[str, Any]: Individual records from the API.

        Raises:
            Exception: If the API response has a status code other than 200.
        """
        url = self._get_url(path)
        while url:
            ret = requests.get(url, headers={"Authorization": f"Token {self.token}"}, timeout=10)
            if ret.status_code != 200:
                raise Exception(f"Error {ret.status_code} fetching {url}")
            data = ret.json()

            for record in data["results"]:
                yield record

            url = data.get("next")
