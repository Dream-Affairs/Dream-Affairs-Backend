"""Schemas for invite endpoints."""

from pydantic import BaseModel, EmailStr


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
    organization_id: str
    role_id: str
