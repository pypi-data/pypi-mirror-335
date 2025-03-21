"""
Task model for the Clockify SDK
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class Task(ClockifyBaseModel):
    """Task model representing a Clockify task."""

    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    project_id: str = Field(..., description="Project ID")
    workspace_id: str = Field(..., description="Workspace ID")
    user_group_id: Optional[str] = Field(None, description="User group ID")
    assignee_id: Optional[str] = Field(None, description="Assignee ID")
    estimate: Optional[str] = Field(
        None, description="Estimated duration in ISO 8601 format"
    )
    status: Literal["ACTIVE", "ALL", "DONE"] = Field(..., description="Task status")
    is_active: bool = Field(True, description="Whether the task is active")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class TaskManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for task-related operations."""

    def get_all(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks in a project.

        Args:
            project_id: ID of the project

        Returns:
            List of tasks
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID.

        Args:
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Task information
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}",
            response_type=Dict[str, Any],
        )

    def create(
        self,
        project_id: str,
        name: str,
        estimate: Optional[str] = None,
        status: Literal["ACTIVE", "ALL", "DONE"] = "ACTIVE",
        assignee_ids: Optional[List[str]] = None,
        user_group_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new task.

        Args:
            project_id: ID of the project
            name: Task name
            estimate: Estimated duration in ISO 8601 format
            status: Task status
            assignee_ids: List of assignee IDs
            user_group_ids: List of user group IDs

        Returns:
            Created task information
        """
        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks",
            json={
                "name": name,
                "estimate": estimate,
                "status": status,
                "assigneeIds": assignee_ids,
                "userGroupIds": user_group_ids,
            },
            response_type=Dict[str, Any],
        )

    def update(
        self,
        project_id: str,
        task_id: str,
        name: Optional[str] = None,
        estimate: Optional[str] = None,
        status: Literal["ACTIVE", "ALL", "DONE"] = "ACTIVE",
        assignee_ids: Optional[List[str]] = None,
        user_group_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing task.

        Args:
            project_id: ID of the project
            task_id: ID of the task
            name: Task name
            estimate: Estimated duration in ISO 8601 format
            status: Task status
            assignee_ids: List of assignee IDs
            user_group_ids: List of user group IDs

        Returns:
            Updated task information
        """
        return self._request(
            "PUT",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}",
            json={
                "name": name,
                "estimate": estimate,
                "status": status,
                "assigneeIds": assignee_ids,
                "userGroupIds": user_group_ids,
            },
            response_type=Dict[str, Any],
        )

    def delete(self, project_id: str, task_id: str) -> None:
        """Delete a task.

        Args:
            project_id: ID of the project
            task_id: ID of the task
        """
        self._request(
            "DELETE",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}",
            response_type=Dict[str, Any],
        )

    def mark_task_done(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Mark a task as done.

        Args:
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Updated task information
        """
        return self.update(project_id, task_id, status="DONE")

    def mark_task_active(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Mark a task as active.

        Args:
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Updated task information
        """
        return self.update(project_id, task_id, status="ACTIVE")
