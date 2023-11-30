"""Schemas for role and permission endpoints."""
from typing import List

from pydantic import BaseModel

from app.services.permission_services import PermissionSchema


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
    permissions: List[PermissionSchema]
