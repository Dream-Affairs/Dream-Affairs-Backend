"""Schemas for invite endpoints."""
from pydantic import BaseModel, EmailStr


class RoleCreate(BaseModel):
    """Schema for creating a new role.

    Attributes:
        name (str): Name of the role
        description (str): Description of the role
        organization_id (str): Organization ID
        permissions (list[str]): List of permissions
    """

    name: str
    description: str
    organization_id: str
    permissions: list[str]


class InviteOrgMember(BaseModel):
    """Schema for inviting a new organization member.

    Attributes:
        email (EmailStr): Email of the user
        organization_id (str): Organization ID
        role (str): Role of the user
    """

    email: EmailStr
    organization_id: str
    role: str
