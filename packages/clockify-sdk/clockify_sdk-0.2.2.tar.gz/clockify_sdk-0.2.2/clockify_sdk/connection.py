"""
Connection manager for the Clockify SDK
"""

from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from clockify_sdk.config import Config
from clockify_sdk.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
)


class ConnectionManager:
    """Connection manager for making HTTP requests to the Clockify API."""

    def __init__(self, api_key: str):
        """Initialize the connection manager.

        Args:
            api_key: Clockify API key
        """
        self.api_key = api_key
        self.timeout = Config.get_timeout()
        self.max_retries = 3
        self.pool_connections = 10
        self.pool_maxsize = 10

        # Create session with connection pooling and retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make an HTTP request to the Clockify API.

        Args:
            method: HTTP method
            url: Request URL
            json: Request body
            params: Query parameters
            headers: Request headers

        Returns:
            API response

        Raises:
            ClockifyError: If the API request fails
        """
        headers = headers or {}
        headers.update({"X-Api-Key": self.api_key, "Content-Type": "application/json"})

        response = self.session.request(
            method=method,
            url=url,
            json=json,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 404:
            raise ResourceNotFoundError("Resource not found")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif not response.ok:
            raise APIError(f"API request failed: {response.text}")

        return response.json()

    def close(self) -> None:
        """Close the connection manager and release resources."""
        self.session.close()
