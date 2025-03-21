"""
User model for the Clockify SDK
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class User(ClockifyBaseModel):
    """User model representing a Clockify user."""

    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    status: str = Field(..., description="User status")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    active_workspace: str = Field(..., description="Active workspace ID")
    default_workspace: str = Field(..., description="Default workspace ID")
    settings: Optional[Dict[str, Any]] = Field(None, description="User settings")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class UserManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for user-related operations."""

    def get_current_user(self) -> Dict[str, Any]:
        """Get the current user.

        Returns:
            Current user information
        """
        return self._request("GET", "user", response_type=Dict[str, Any])

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all users in a workspace.

        Returns:
            List of users in the workspace
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/users",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get a specific user by ID.

        Args:
            user_id: ID of the user

        Returns:
            User information
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/users/{user_id}",
            response_type=Dict[str, Any],
        )

    def set_active_workspace(self) -> Dict[str, Any]:
        """Set the active workspace for the current user.

        Returns:
            Updated user information
        """
        return self._request(
            "PUT", f"users/workspaces/{self.workspace_id}", response_type=Dict[str, Any]
        )
