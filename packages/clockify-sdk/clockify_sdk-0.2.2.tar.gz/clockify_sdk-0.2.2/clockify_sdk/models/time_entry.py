"""Time entry management for Clockify API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from ..connection import ConnectionManager
from ..utils.date_utils import format_datetime
from .base import ClockifyBaseModel


class TimeEntry(ClockifyBaseModel):
    """Time entry model representing a Clockify time entry."""

    id: str = Field(..., description="Time entry ID")
    description: str = Field(..., description="Time entry description")
    project_id: Optional[str] = Field(None, description="Project ID")
    task_id: Optional[str] = Field(None, description="Task ID")
    user_id: str = Field(..., description="User ID")
    workspace_id: str = Field(..., description="Workspace ID")
    start: datetime = Field(..., description="Start time")
    end: Optional[datetime] = Field(None, description="End time")
    duration: Optional[str] = Field(None, description="Duration in ISO 8601 format")
    billable: bool = Field(False, description="Whether the time entry is billable")
    tags: List[str] = Field(default_factory=list, description="List of tag IDs")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class TimeEntryManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for time entry-related operations."""

    def __init__(
        self, connection_manager: ConnectionManager, workspace_id: Optional[str] = None
    ) -> None:
        """Initialize the time entry manager.

        Args:
            connection_manager: Connection manager for making HTTP requests
            workspace_id: Optional workspace ID to use for requests
        """
        super().__init__(connection_manager, workspace_id)

    def get_all_in_progress(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all time entries in the workspace.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of time entries
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/time-entries/status/in-progress",
            response_type=List[Dict[str, Any]],
        )

    def get_by_user_id(
        self,
        user_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        project_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all time entries by user ID.

        Args:
            user_id: User ID to filter by

        Returns:
            List of time entries
        """
        params = {}
        if start:
            params["start"] = format_datetime(start)
        if end:
            params["end"] = format_datetime(end)
        if project_ids:
            params["projectIds"] = ",".join(project_ids)

        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/user/{user_id}/time-entries",
            params=params,
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, time_entry_id: str) -> Dict[str, Any]:
        """Get a specific time entry by ID.

        Args:
            time_entry_id: ID of the time entry

        Returns:
            Time entry information
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/time-entries/{time_entry_id}",
            response_type=Dict[str, Any],
        )

    def create(
        self,
        start: datetime,
        end: Optional[datetime] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        description: Optional[str] = None,
        billable: bool = False,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new time entry.

        Args:
            start: Start time
            end: End time
            project_id: Optional project ID
            task_id: Optional task ID
            description: Optional description
            billable: Whether the time entry is billable
            tags: Optional list of tag IDs

        Returns:
            Created time entry information
        """
        data: Dict[str, Any] = {
            "start": format_datetime(start),
            "end": format_datetime(end) if end else None,
            "description": description,
            "projectId": project_id,
            "taskId": task_id,
            "billable": billable,
            "tags": tags,
        }

        response = self._request(
            "POST",
            f"workspaces/{self.workspace_id}/time-entries",
            json=data,
            response_type=Dict[str, Any],
        )
        return response

    def update(
        self,
        time_entry_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        description: Optional[str] = None,
        billable: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing time entry.

        Args:
            time_entry_id: ID of the time entry
            start: Start time
            end: End time
            project_id: Project ID
            task_id: Task ID
            description: Description
            billable: Whether the time entry is billable
            tags: List of tag IDs

        Returns:
            Updated time entry information
        """
        data: Dict[str, Any] = {
            "start": format_datetime(start) if start else None,
            "end": format_datetime(end) if end else None,
            "projectId": project_id,
            "taskId": task_id,
            "description": description,
            "billable": billable,
            "tags": tags,
        }
        # Remove keys with None values
        data = {k: v for k, v in data.items() if v is not None}

        return self._request(
            "PUT",
            f"workspaces/{self.workspace_id}/time-entries/{time_entry_id}",
            json=data,
            response_type=Dict[str, Any],
        )

    def delete(self, time_entry_id: str) -> None:
        """Delete a time entry.

        Args:
            time_entry_id: ID of the time entry
        """
        self._request(
            "DELETE",
            f"workspaces/{self.workspace_id}/time-entries/{time_entry_id}",
            response_type=Dict[str, Any],
        )

    def start_timer(
        self,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start a timer.

        Args:
            project_id: Project ID
            task_id: Task ID
            description: Description

        Returns:
            Started timer information
        """
        response = self._request(
            "POST",
            f"workspaces/{self.workspace_id}/time-entries/timer/start",
            json={
                "projectId": project_id,
                "taskId": task_id,
                "description": description,
            },
            response_type=Dict[str, Any],
        )
        return response

    def stop_timer(
        self,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stop a timer.

        Args:
            project_id: Project ID
            task_id: Task ID
            description: Description

        Returns:
            Stopped timer information
        """
        response = self._request(
            "POST",
            f"workspaces/{self.workspace_id}/time-entries/timer/stop",
            json={
                "projectId": project_id,
                "taskId": task_id,
                "description": description,
            },
            response_type=Dict[str, Any],
        )
        return response

    def get_current_timer(self) -> Dict[str, Any]:
        """Get the current timer.

        Returns:
            Current timer information
        """
        response = self._request(
            "GET",
            f"workspaces/{self.workspace_id}/time-entries/timer",
            response_type=Dict[str, Any],
        )
        return response
