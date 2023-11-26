"""Schemas for role and permission endpoints."""
from typing import List

from pydantic import BaseModel


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
    permission_class: str
    permissions: List[str]
