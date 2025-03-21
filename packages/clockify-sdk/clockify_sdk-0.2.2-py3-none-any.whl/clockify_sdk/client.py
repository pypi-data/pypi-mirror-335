"""
Clockify SDK client implementation
"""

from typing import Any, Dict, List, Optional, cast

from .config import Config
from .connection import ConnectionManager
from .models.client import ClientManager
from .models.project import ProjectManager
from .models.report import ReportManager
from .models.task import TaskManager
from .models.time_entry import TimeEntryManager
from .models.user import UserManager


class Clockify:
    """
    Main entry point for interacting with the Clockify API.
    Provides a standardized interface for all Clockify operations.

    Args:
        api_key: Your Clockify API key. Can also be set via CLOCKIFY_API_KEY environment variable.
        workspace_id: Optional workspace ID to use. If not provided, uses the first available workspace.
    """

    def __init__(self, api_key: str, workspace_id: Optional[str] = None) -> None:
        """
        Initialize the Clockify client with your API key

        Args:
            api_key: Your Clockify API key. If not provided, will look for CLOCKIFY_API_KEY environment variable.
            workspace_id: Optional workspace ID to use. If not provided, uses the first available workspace.

        Raises:
            ValueError: If no API key is provided and CLOCKIFY_API_KEY environment variable is not set.
        """
        self.api_key: str = api_key
        self.workspace_id: Optional[str] = None
        self.user_id: str = ""

        Config.set_api_key(api_key)
        self._connection = ConnectionManager(api_key)

        # Initialize managers
        self.users = UserManager(self._connection)
        self.time_entries = TimeEntryManager(self._connection)
        self.projects = ProjectManager(self._connection)
        self.reports = ReportManager(self._connection)
        self.clients = ClientManager(self._connection)
        self.tasks = TaskManager(self._connection)

        # Get user info
        user = self.users.get_current_user()
        self.user_id = user["id"]

        # Set workspace ID
        if workspace_id:
            self.workspace_id = workspace_id
        else:
            workspaces = self.get_workspaces()
            self.workspace_id = workspaces[0]["id"] if workspaces else None

        # Update all managers with workspace ID
        for manager in [
            self.users,
            self.time_entries,
            self.projects,
            self.reports,
            self.clients,
            self.tasks,
        ]:
            manager.workspace_id = self.workspace_id

    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces for the current user.

        Returns:
            List of workspace objects.
        """
        response = self._connection.request(
            method="GET",
            url=f"{Config.BASE_URL}/workspaces",
        )
        return cast("List[Dict[str, Any]]", response)

    def close(self) -> None:
        """Close all connections."""
        self._connection.close()

    def __enter__(self) -> "Clockify":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Context manager exit."""
        self.close()
