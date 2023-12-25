"""Schemas for invite endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class OrganizationEvent(BaseModel):
    """Schema for event details.

    Attributes:
        event_date (datetime): Date of the event
        location (str): Location of the event
        event_start_time (datetime): Start time of the event
        event_end_time (datetime): End time of the event
    """

    event_location: str
    website: Optional[str] = None
    event_date: Optional[datetime] = None
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None

    @field_validator("website", check_fields=True)
    # pylint: disable=no-self-argument
    def validate_website(cls, website: str):
        """Add forward to website.

        Args:
            website (str): Website
        """
        if website and not website.startswith("/"):
            website = f"/{website}"

        return website


class OrganizationCreate(BaseModel):
    """Schema for creating an organization.

    Attributes:
        name (str): Name of the organization
        description (str): Description of the organization
        website (str): Website of the organization
        logo (str): Logo of the organization
        event_details (OrganizationEvent): Event details
    """

    name: str
    description: Optional[str] = None
    event_type: Optional[str] = "Wedding"
    logo: Optional[str] = None
    event_details: Optional[OrganizationEvent] = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization.

    Attributes:
        name (str): Name of the organization
        description (str): Description of the organization
        website (str): Website of the organization
        logo (str): Logo of the organization
        event_details (OrganizationEvent): Event details
    """

    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    event_details: OrganizationEvent


class InviteMemberSchema(BaseModel):  # type: ignore
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


class AuthorizeOrganizationSchema(BaseModel):
    """Data model for an organization.

    Attributes:
        name (str): The name of the organization.
        owner (str): The ID of the owner of the organization.
        id (str): The id of
    """

    id: str
    name: str
    account_id: str
    organization_id: str
