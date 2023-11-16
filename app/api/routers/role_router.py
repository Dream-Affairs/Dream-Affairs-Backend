from fastapi import APIRouter, Depends
from app.api.schemas.invite_schemas import RoleCreate
from app.api.models.organization_models import OrganizationRole
from app.api.models.role_permission_models import RolePermission, Permission
from app.database.connection import get_db

router = APIRouter(tags=["Roles & Permissions"])


@router.get("/permissions")
async def get_permissions(db=Depends(get_db)):
    """
    Get all permissions

    Returns:
        list: A list of permissions
    """
    permissions = db.query(Permission).all()
    return permissions


@router.get("/roles")
async def get_roles(db=Depends(get_db)):
    """
    Get all roles

    Returns:
        list: A list of roles
    """
    roles = db.query(OrganizationRole).all()
    return roles


@router.post("/roles")
async def create_role(role: RoleCreate, db=Depends(get_db)):
    """
    Create a new role

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

    for permission in role.permissions:
        new_permission = RolePermission(
            role_id=new_role.id, permission_id=permission
        )
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
