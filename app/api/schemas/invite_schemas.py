"""Schemas for invite endpoints."""
from typing import List

from pydantic import BaseModel, EmailStr


class RoleCreate(BaseModel):  # type: ignore
    """Schema for creating a new role.

    Attributes:
        name (str): Name of the role
        description (str): Description of the role
        organization_id (str): Organization ID
        permissions (List[str]): List of permissions
    """

    name: str
    description: str
    organization_id: str
    permissions: List[str]


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
