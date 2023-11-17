from sqlalchemy.orm.session import Session

from app.api.models.organization_models import Organization, OrganizationRole
from app.api.models.role_permission_models import Permission, RolePermission
from app.services.custom_services import model_to_dict
from app.api.responses.custom_responses import CustomException
from uuid import uuid4


def create_new_role(db: Session, role: dict):
    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == role.organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": role.organization_id},
        )

    # Check if role with same name exists
    role_exists = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == role.organization_id)
        .filter(OrganizationRole.name == role.name)
        .first()
    )
    if role_exists:
        raise CustomException(
            status_code=400,
            message="Role with same name already exists",
            data={"role_name": role.name},
        )

    new_role = OrganizationRole(
        name=role.name,
        description=role.description,
        organization_id=role.organization_id,
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    permissions = []

    try:
        for permission_id in role.permissions:
            permission = (
                db.query(Permission)
                .filter(Permission.id == permission_id)
                .first()
            )
            if not permission:
                raise CustomException(
                    status_code=400,
                    message="Permission does not exist",
                    data={
                        "permission_id": permission_id
                    }
                )
            new_permission = RolePermission(
                id=uuid4().hex,
                organization_role_id=new_role.id,
                permission_id=permission_id,
            )
            db.add(new_permission)
            db.commit()
            db.refresh(new_permission)

            permissions.append({
                "id": permission_id,
                "name": permission.name,
                "description": permission.description,
            })
    except Exception:
        raise CustomException(
            status_code=400,
            message="Failed to create role",
            data={"permission_id": permission_id},
        )

    return {
        "id": new_role.id,
        "name": new_role.name,
        "description": new_role.description,
        "permissions": permissions,
    }


def get_all_roles(db: Session, organization_id: str):
    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )
    roles = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .all()
    )

    roles_dict = model_to_dict(roles)

    return roles_dict

    return roles


def get_role_details(db: Session, organization_id: str, role_id: str):
    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    # Check if role exists
    role = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .filter(OrganizationRole.id == role_id)
        .first()
    )
    if not role:
        raise CustomException(
            status_code=404,
            message="Role not found",
            data={"role_id": role_id},
        )

    # Get role permissions
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
