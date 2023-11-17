from uuid import uuid4

from fastapi import APIRouter, Depends

from app.api.models.organization_models import OrganizationRole
from app.api.models.role_permission_models import Permission, RolePermission
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.invite_schemas import RoleCreate
from app.database.connection import get_db
from app.services.custom_services import model_to_dict

router = APIRouter(tags=["Roles & Permissions"])


@router.get("/permissions")
async def get_permissions(db=Depends(get_db)):
    """Get all permissions.

    Returns:
        list: A list of permissions
    """
    permissions = db.query(Permission).all()
    permissions_dict = model_to_dict(permissions)
    return CustomResponse(
        status_code=200,
        message="Permissions retrieved successfully",
        data=permissions_dict,
    )


@router.get("/roles/{organization_id}")
async def get_role(organization_id: str, db=Depends(get_db)):
    """Get all role for an organization.

    Args:
        organization_id (int): The organization id

    Returns:
        Role: The role
    """
    role = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .all()
    )
    return role


@router.get("/roles/{organization_id}/{role_id}")
async def get_role(organization_id: str, role_id: str, db=Depends(get_db)):
    """Get a role for an organization.

    Args:
        organization_id (int): The organization id
        role_id (int): The role id

    Returns:
        Role: The role
    """
    role = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .filter(OrganizationRole.id == role_id)
        .first()
    )

    if not role:
        return {"error": "Role not found"}

    print(role.id)
    role_permissions = (
        db.query(RolePermission)
        .filter(RolePermission.organization_role_id == role.id)
        .all()
    )

    return role_permissions


from uuid import uuid4


@router.post("/roles")
async def create_role(role: RoleCreate, db=Depends(get_db)):
    """Create a new role.

    Args:
        role (RoleCreate): The role to be created

    Returns:
        Role: The created role
    """
    new_role = OrganizationRole(
        name=role.name,
        description=role.description,
        organization_id=role.organization_id,
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    try:
        for permission in role.permissions:
            new_permission = RolePermission(
                id=uuid4().hex,
                organization_role_id=new_role.id,
                permission_id=permission,
            )
            print(new_permission.id)
            print(new_permission.organization_role_id)
            print(new_permission.permission_id)
            print("New Permission")
            db.add(new_permission)
            db.commit()
            db.refresh(new_permission)
    except Exception as e:
        return {"error": str(e)}

    return new_role
