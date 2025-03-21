"""
Client model for the Clockify SDK
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class Client(ClockifyBaseModel):
    """Client model representing a Clockify client."""

    id: str = Field(..., description="Client ID")
    name: str = Field(..., description="Client name")
    workspace_id: str = Field(..., description="Workspace ID")
    note: Optional[str] = Field(None, description="Client note")
    address: Optional[str] = Field(None, description="Client address")
    email: Optional[str] = Field(None, description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    website: Optional[str] = Field(None, description="Client website")
    is_archived: bool = Field(False, description="Whether the client is archived")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class ClientManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for client-related operations."""

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all clients in the workspace.

        Returns:
            List of clients
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/clients",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, client_id: str) -> Dict[str, Any]:
        """Get a specific client by ID.

        Args:
            client_id: ID of the client

        Returns:
            Client information
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/clients/{client_id}",
            response_type=Dict[str, Any],
        )

    def create(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new client.

        Args:
            name: Client name
            email: Client email
            address: Client address
            note: Client note

        Returns:
            Created client information
        """

        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/clients",
            json={"name": name, "email": email, "address": address, "note": note},
            response_type=Dict[str, Any],
        )

    def update(
        self,
        client_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing client.

        Args:
            client_id: ID of the client
            name: Client name
            email: Client email
            address: Client address
            note: Client note

        Returns:
            Updated client information
        """
        return self._request(
            "PUT",
            f"workspaces/{self.workspace_id}/clients/{client_id}",
            json={"name": name, "email": email, "address": address, "note": note},
            response_type=Dict[str, Any],
        )

    def delete(self, client_id: str) -> None:
        """Delete a client.

        Args:
            client_id: ID of the client
        """
        self._request(
            "DELETE",
            f"workspaces/{self.workspace_id}/clients/{client_id}",
            response_type=Dict[str, Any],
        )
