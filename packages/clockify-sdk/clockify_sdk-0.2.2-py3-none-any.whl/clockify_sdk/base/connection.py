"""
Connection manager for the Clockify SDK
"""

from typing import Any, Dict, Optional

import requests


class ConnectionManager:
    """Connection manager for making HTTP requests to the Clockify API."""

    def __init__(self, api_key: str):
        """Initialize the connection manager.

        Args:
            api_key: Clockify API key
        """
        self.api_key = api_key

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

        response = requests.request(
            method=method, url=url, json=json, params=params, headers=headers
        )

        if response.status_code >= 400:
            raise Exception(
                f"API request failed: {response.status_code} - {response.text}"
            )

        return response.json()

    def close(self) -> None:
        """Close any open connections."""
        pass
