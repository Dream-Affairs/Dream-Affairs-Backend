from app.api.models.role_permission_models import Permission, RolePermission
from app.api.models.organization_models import OrganizationRole
from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from app.services.custom_services import model_to_dict

def get_all_roles(db: Session, organization_id: str):
    roles = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .all()
    )

    roles_dict = model_to_dict(roles)

    return roles_dict

    return roles
def get_role_details(db: Session, organization_id: str, role_id: str):
    role = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .filter(OrganizationRole.id == role_id)
        .first()
    )

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role_permissions = (
        db.query(RolePermission)
        .filter(RolePermission.organization_role_id == role.id)
        .all()
    )

    permissions = []

    for role_permission in role_permissions:
        permission_details = (
            db.query(Permission)
            .filter(Permission.id == role_permission.permission_id)
            .first()
        )

        if permission_details:
            permissions.append(
                {
                    "id": permission_details.id,
                    "name": permission_details.name,
                    "description": permission_details.description,
                }
            )

    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "permissions": permissions,
    }