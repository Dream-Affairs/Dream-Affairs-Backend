"""This module contains the schemas for the checklist route."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ChecklistStatus(str, Enum):
    """Enum for checklist status."""

    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ChecklistSortBy(str, Enum):
    """Enum for checklist sort by."""

    ALL = "all"
    DUE_DATE = "due_date"
    ASSIGNED_TO_ME = "assigned_to_me"
    ASSIGNED_BY_ME = "assigned_by_me"


class ChelistSortOrder(str, Enum):
    """Enum for checklist sort order."""

    ASC = "asc"
    DESC = "desc"


class ChecklistBase(BaseModel):  # type: ignore
    """Base schema for a checklist."""

    title: str
    description: Optional[str] | None


class ChecklistCreate(ChecklistBase):
    """Schema for creating a checklist."""

    assigned_to: Optional[str] | None = None
    created_by: str
    organization_id: str
    status: ChecklistStatus

    due_date: Optional[datetime] | str = "Example(2021-09-01T00:00:00.000Z)"

    class Config:
        """Config for the schema."""

        json_schema_extra = {
            "example": {
                "title": "Checklist title",
                "description": "Checklist description" or None,
                "assigned_to": "" or None,
                "created_by": "member_id",
                "organization_id": "organization_id",
                "status": "pending",
                "due_date": "Example(2021-09-01T00:00:00.000Z)" or None,
            }
        }


class ChecklistUpdate(BaseModel):  # type: ignore
    """Schema for updating a checklist."""

    kwargs: Dict[str, Any]


class ChecklistDelete(BaseModel):  # type: ignore
    """Schema for deleting a checklist."""

    id: str


class ChecklistGetAll(BaseModel):  # type: ignore
    """Schema for getting all checklists."""


class ChecklistResponse(BaseModel):  # type: ignore
    """Schema for a checklist response."""

    id: str
    title: str
    description: str | None
    assigned_to: str | None
    created_by: str
    organization_id: str
    status: str
    due_date: datetime
    created_at: datetime
