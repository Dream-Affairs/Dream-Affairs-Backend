"""This module contains the schemas for the checklist route."""
from datetime import datetime

from pydantic import BaseModel


class ChecklistBase(BaseModel):  # type: ignore
    """Base schema for a checklist."""

    title: str
    description: str


class ChecklistCreate(ChecklistBase):
    """Schema for creating a checklist."""

    assigned_to: str
    created_by: str
    organization_id: str
    status: str
    due_date: datetime


class ChecklistUpdate(ChecklistBase):
    """Schema for updating a checklist."""


class ChecklistDelete(BaseModel):  # type: ignore
    """Schema for deleting a checklist."""

    id: str


class ChecklistGet(BaseModel):  # type: ignore
    """Schema for getting a checklist."""

    id: str


class ChecklistGetAll(BaseModel):  # type: ignore
    """Schema for getting all checklists."""


class ChecklistResponse(BaseModel):  # type: ignore
    """Schema for a checklist response."""

    id: str
    title: str
    description: str
    assigned_to: str
    created_by: str
    organization_id: str
    status: str
    due_date: datetime
    created_at: datetime
