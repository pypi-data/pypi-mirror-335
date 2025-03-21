"""
Base client for the Clockify SDK
"""

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from ..config import Config
from ..connection import ConnectionManager
from ..logging import logger

SingleResponse = TypeVar("SingleResponse", bound=Dict[str, Any])
ListResponse = TypeVar("ListResponse", bound=List[Dict[str, Any]])


class ApiClientBase(Generic[SingleResponse, ListResponse]):
    """Base class for making requests to the Clockify API.
    Provides common functionality for API clients."""

    def __init__(
        self, connection_manager: ConnectionManager, workspace_id: Optional[str] = None
    ):
        """Initialize the base client.

        Args:
            connection_manager: Connection manager for making HTTP requests
            workspace_id: Optional workspace ID to use for requests
        """
        self._connection = connection_manager
        self.workspace_id = workspace_id

    def _get_workspace_id(self, workspace_id: Optional[str] = None) -> str:
        """Get the workspace ID to use for requests.

        Args:
            workspace_id: Optional workspace ID to override the default

        Returns:
            The workspace ID to use

        Raises:
            ValueError: If no workspace ID is available
        """
        if workspace_id:
            return workspace_id
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before making requests")
        return self.workspace_id

    @overload
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_type: Type[SingleResponse],
        is_reports: bool = False,
    ) -> SingleResponse: ...

    @overload
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_type: Type[ListResponse],
        is_reports: bool = False,
    ) -> ListResponse: ...

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_type: Union[Type[SingleResponse], Type[ListResponse]],
        is_reports: bool = False,
    ) -> Union[SingleResponse, ListResponse]:
        """Make a request to the Clockify API.

        Args:
            method: HTTP method
            path: API path
            json: Request body
            params: Query parameters
            response_type: Expected response type
            is_reports: Whether the request is for reports
        Returns:
            API response

        Raises:
            ClockifyError: If the API request fails
        """
        url = f"{Config.BASE_URL if not is_reports else Config.REPORTS_URL}/{path}"
        try:
            response = self._connection.request(
                method=method, url=url, json=json, params=params
            )
            if response_type == List[Dict[str, Any]]:
                return cast("ListResponse", response)
            return cast("SingleResponse", response)
        except Exception as e:
            logger.error(f"API request failed: {e!s}")
            raise

    def close(self) -> None:
        """Close the session"""
        self._connection.close()
