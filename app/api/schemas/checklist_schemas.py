"""This module contains the schemas for the checklist route."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ChecklistStatus(str, Enum):
    """Enum for checklist status."""

    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ChecklistSortBy(str, Enum):
    """Enum for checklist sort by."""

    ALL = "all"
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

    due_date: Optional[datetime] | None = None


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
    due_date: datetime | None
    created_at: datetime
