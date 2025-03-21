"""
Report model for the Clockify SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from ..utils.date_utils import format_datetime
from .base import ClockifyBaseModel


class Report(ClockifyBaseModel):
    """Report model representing a Clockify report."""

    id: str = Field(..., description="Report ID")
    name: str = Field(..., description="Report name")
    workspace_id: str = Field(..., description="Workspace ID")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    project_ids: List[str] = Field(
        default_factory=list, description="List of project IDs"
    )
    user_ids: List[str] = Field(default_factory=list, description="List of user IDs")
    task_ids: List[str] = Field(default_factory=list, description="List of task IDs")
    tag_ids: List[str] = Field(default_factory=list, description="List of tag IDs")
    billable: Optional[bool] = Field(
        None, description="Whether to include billable time entries"
    )
    description: Optional[str] = Field(None, description="Report description")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )
    date_range_start: str = Field(..., description="Start date in datetime format")
    date_range_end: str = Field(..., description="End date in datetime format")
    amount_shown: Optional[str] = Field(
        None, description="Enum: EARNED, COST, PROFIT, HIDE_AMOUNT, EXPORT"
    )
    amounts: List[str] = Field(default_factory=list, description="Array of amounts")
    approval_state: Optional[str] = Field(
        None, description="Enum: APPROVED, UNAPPROVED, ALL"
    )
    archived: Optional[bool] = Field(
        None, description="Indicates whether the report is archived"
    )


class ReportSummary(ClockifyBaseModel):
    """Model representing a summary report from Clockify."""

    totals: List[Dict[str, Any]] = Field(
        default_factory=list, description="Summary totals"
    )
    groups: List[Dict[str, Any]] = Field(
        default_factory=list, description="Grouped data"
    )


class ReportManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for report-related operations."""

    def get_summary(
        self,
        start: datetime,
        end: datetime,
        user_ids: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        group_by: Optional[List[str]] = None,
        sort_column: str = "GROUP",
    ) -> Dict[str, Any]:
        """Get a summary of the report.

        Args:
            start: Start date
            end: End date
            user_ids: Optional list of user IDs to filter by
            project_ids: Optional list of project IDs to filter by
            group_by: List of fields to group by (PROJECT, CLIENT, TAG, etc.)
            sort_column: Column to sort by

        Returns:
            Summary of the report
        """

        data = {
            "dateRangeStart": format_datetime(start),
            "dateRangeEnd": format_datetime(end),
            "summaryFilter": {
                "groups": group_by,
                "sortColumn": sort_column,
            },
            "exportType": "JSON",
        }

        if user_ids:
            data["userIds"] = user_ids

        if project_ids:
            data["projectIds"] = project_ids

        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/reports/summary",
            json=data,
            response_type=Dict[str, Any],
            is_reports=True,
        )

    def get_detailed(
        self,
        start: datetime,
        end: datetime,
        user_ids: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        page_size: int = 50,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Get detailed report data.

        Args:
            start: Start date
            end: End date
            user_ids: Optional list of user IDs to filter by
            project_ids: Optional list of project IDs to filter by
            page_size: Number of results per page
            page: Page number

        Returns:
            Detailed report data
        """

        data = {
            "dateRangeStart": format_datetime(start),
            "dateRangeEnd": format_datetime(end),
            "detailedFilter": {
                "page": page,
                "pageSize": page_size,
                "sortColumn": "DATE",
            },
            "exportType": "JSON",
        }

        if user_ids:
            data["userIds"] = user_ids

        if project_ids:
            data["projectIds"] = project_ids

        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/reports/detailed",
            json=data,
            response_type=Dict[str, Any],
            is_reports=True,
        )
