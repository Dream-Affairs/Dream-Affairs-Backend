"""This module defines the router for the role endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.api.models.role_permission_models import Permission
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.invite_schemas import RoleCreate
from app.database.connection import get_db
from app.services.custom_services import model_to_dict
from app.services.roles_services import (
    create_new_role,
    get_all_roles,
    get_role_details,
)

router = APIRouter(tags=["Roles & Permissions"])


@router.get("/permissions")
async def get_permissions(db: Session = Depends(get_db)) -> CustomResponse:
    """Get all permissions.

    Args:
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        CustomResponse: List of Permission
    """
    permissions = model_to_dict(db.query(Permission).all())
    return CustomResponse(
        status_code=200,
        message="Permissions retrieved successfully",
        data=permissions,
    )


@router.get("/roles/{organization_id}")
async def get_roles(
    organization_id: str, db: Session = Depends(get_db)
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
        roles = get_all_roles(db, organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Roles retrieved successfully",
        data=roles,
    )


@router.get("/roles/{organization_id}/{role_id}")
async def get_role_by_id(
    organization_id: str, role_id: str, db: Session = Depends(get_db)
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
        role_details = get_role_details(db, organization_id, role_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Role retrieved successfully",
        data=role_details,
    )


@router.post("/roles")
async def create_role(
    role: RoleCreate, db: Session = Depends(get_db)
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
    try:
        role_details = create_new_role(db, role)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Role created successfully",
        data=role_details,
    )
