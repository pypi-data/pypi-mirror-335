"""
Configuration for the Clockify SDK
"""

import os


class Config:
    """Configuration for the Clockify SDK."""

    _api_key: str = ""
    BASE_URL: str = "https://api.clockify.me/api/v1"
    REPORTS_URL: str = "https://reports.api.clockify.me/v1"

    # Default settings
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_PAGE_SIZE = 50

    # Date format settings
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """Set the API key.

        Args:
            api_key: Clockify API key
        """
        cls._api_key = api_key

    @classmethod
    def get_api_key(cls) -> str:
        """Get the API key.

        Returns:
            Clockify API key
        """
        return cls._api_key

    @classmethod
    def get_timeout(cls) -> int:
        """Get the default timeout for API requests"""
        return int(os.getenv("CLOCKIFY_TIMEOUT", cls.DEFAULT_TIMEOUT))

    @classmethod
    def get_page_size(cls) -> int:
        """Get the default page size for paginated requests"""
        return int(os.getenv("CLOCKIFY_PAGE_SIZE", cls.DEFAULT_PAGE_SIZE))
