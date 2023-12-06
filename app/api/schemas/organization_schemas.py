"""Schemas for invite endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Organizationevent(BaseModel):
    """Schema for event details.

    Attributes:
        event_date (datetime): Date of the event
        location (str): Location of the event
        event_start_time (datetime): Start time of the event
        event_end_time (datetime): End time of the event
    """

    website: Optional[str] = None
    event_date: Optional[datetime] = None
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization.

    Attributes:
        name (str): Name of the organization
        description (str): Description of the organization
        website (str): Website of the organization
        logo (str): Logo of the organization
        event_details (Organizationevent): Event details
    """

    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    event_details: Organizationevent


class InviteMember(BaseModel):  # type: ignore
    """Schema for inviting a new organization member.

    Attributes:
        name (str): Name of the user
        email (EmailStr): Email of the user
        organization_id (str): Organization ID
        role_id (str): Role of the user
    """

    name: str
    email: EmailStr
    role_id: str
