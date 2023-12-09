"""This module defines the router for the role endpoints."""
from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.session import Session

from app.api.middlewares.authorization import (
    Authorize,
    is_authenticated,
    is_org_authorized,
)
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.role_schemas import RoleCreate
from app.database.connection import get_db
from app.services.permission_services import (
    PermissionManager,
    PermissionSchema,
)
from app.services.roles_services import RoleService

router = APIRouter(tags=["Roles and Permissions"])


@router.get("/permissions")
async def get_permissions(
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_authenticated
    ),
) -> CustomResponse:
    """Get all permissions.

    Args:
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        CustomResponse: List of Permission
    """
    permissions, _ = PermissionManager().get_all_permissions(db=db)

    return CustomResponse(
        status_code=200,
        message="Permissions retrieved successfully",
        data=permissions,
    )


@router.get("/role/{organization_id}")
async def get_roles(
    db: Session = Depends(get_db), auth: Authorize = Depends(is_org_authorized)
) -> CustomResponse:
    """Get all roles.

    Args:
        organization_id (str): Organization ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: List of all roles
    """
    try:
        roles = RoleService(
            organization_id=auth.member.organization_id,
        ).get_all_organization_roles(db)

    except Exception as e:
        raise CustomException(
            status_code=400,
            message="Failed to retrieve roles",
        ) from e

    return CustomResponse(
        status_code=200,
        message="Roles retrieved successfully",
        data=roles,
    )


@router.get("/role/{role_id}")
async def get_role_by_id(
    role_id: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> CustomResponse:
    """Get role by ID.

    Args:
        organization_id (str): Organization ID
        role_id (str): Role ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization or role does not exist

    Returns:
        CustomResponse: Role details
    """
    try:
        role = RoleService().get_role(db, role_id)

    except Exception as e:
        print(e)
        raise CustomException(
            status_code=400,
            message="Failed to retrieve role",
        ) from e

    return CustomResponse(
        status_code=200,
        message="Role retrieved successfully",
        data=role,
    )


@router.post("/role")
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> CustomResponse:
    """Create a new role.

    Args:
        role (RoleCreate): Role details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Role details
    """
    if role.organization_id in ("", "string"):
        raise CustomException(
            status_code=400,
            message="Organization ID is required",
        )
    try:
        role_instance = RoleService(
            name=role.name,
            description=role.description,
            is_default=False,
            is_super_admin=False,
            permissions=role.permissions,
            organization_id=role.organization_id,
        ).create_role(db)

    except Exception as e:
        print(e)

        raise CustomException(
            status_code=400,
            message="Failed to create role",
        ) from e

    return CustomResponse(
        status_code=200,
        message="Role created successfully",
        data=jsonable_encoder(role_instance),
    )


@router.put("/role/{role_id}")
async def update_role_permissions(
    role_id: str,
    permissions: List[PermissionSchema],
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> CustomResponse:
    """Update role permissions.

    Args:
        role_id (str): Role ID
        permissions (PermissionManager): Permission details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If role does not exist

    Returns:
        CustomResponse: Role details
    """
    try:
        role = RoleService(
            permissions=permissions,
        ).update_role_permissions(db, role_id)
    except Exception as e:
        raise CustomException(
            status_code=400,
            message="Failed to update role permissions",
        ) from e
    return CustomResponse(
        status_code=200,
        message="Role permissions updated successfully",
        data=role,
    )
