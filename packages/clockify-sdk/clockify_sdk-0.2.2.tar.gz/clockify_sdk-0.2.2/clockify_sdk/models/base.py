"""
Base Pydantic models for the Clockify SDK
"""

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field


class ClockifyBaseModel(BaseModel):
    """Base model for all Clockify models"""

    class Config:
        json_encoders: ClassVar[Dict[type, Any]] = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")
        }


class TimeRange(BaseModel):
    """Model for time range parameters"""

    start: datetime = Field(..., description="Start time of the range")
    end: datetime = Field(..., description="End time of the range")


class PaginationParams(BaseModel):
    """Model for pagination parameters"""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")


class SortParams(BaseModel):
    """Model for sorting parameters"""

    sort_field: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field(
        None, pattern="^(asc|desc)$", description="Sort order (asc/desc)"
    )


class FilterParams(BaseModel):
    """Model for filtering parameters"""

    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    project_ids: Optional[List[str]] = Field(
        None, description="List of project IDs to filter by"
    )
    user_ids: Optional[List[str]] = Field(
        None, description="List of user IDs to filter by"
    )
    client_ids: Optional[List[str]] = Field(
        None, description="List of client IDs to filter by"
    )
    task_ids: Optional[List[str]] = Field(
        None, description="List of task IDs to filter by"
    )
