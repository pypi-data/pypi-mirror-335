"""
Custom exceptions for the Clockify SDK
"""

from typing import Any, Dict, Optional


class ClockifyError(Exception):
    """Base exception for all Clockify SDK errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(ClockifyError):
    """Raised when there are issues with API authentication"""

    pass


class ValidationError(ClockifyError):
    """Raised when there are issues with input validation"""

    pass


class ResourceNotFoundError(ClockifyError):
    """Raised when a requested resource is not found"""

    pass


class RateLimitError(ClockifyError):
    """Raised when the API rate limit is exceeded"""

    pass


class WorkspaceError(ClockifyError):
    """Raised when there are issues with workspace operations"""

    pass


class APIError(ClockifyError):
    """Raised for general API errors"""

    pass
