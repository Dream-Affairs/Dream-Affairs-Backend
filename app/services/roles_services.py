"""Role services."""
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from app.api.models.organization_models import Organization, OrganizationRole
from app.api.models.role_permission_models import Permission, RolePermission
from app.api.responses.custom_responses import CustomException
from app.api.schemas.role_schemas import RoleCreate
from app.services.custom_services import model_to_dict
from app.services.permission_services import PermissionManager

back_task = BackgroundTasks()


def create_new_role(db: Session, role: RoleCreate) -> Dict[str, Any]:
    """Create new role.

    Args:
        db (Session): Database session
        role (dict): Role details

    Raises:
        CustomException: If organization does not exist
        CustomException: If role with same name already exists
        CustomException: If permission does not exist

    Returns:
        dict: Role details
    """
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

    # Create new role
    try:
        new_role = OrganizationRole(
            name=role.name,
            description=role.description,
            organization_id=role.organization_id,
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to create new role",
            data={"role_id": role.id},
        ) from exc

    permissions = []

    for permission_id in role.permissions:
        # Check if permission exists
        permission = (
            db.query(Permission).filter(Permission.id == permission_id).first()
        )
        if not permission:
            raise CustomException(
                status_code=400,
                message="Permission does not exist",
                data={"permission_id": permission_id},
            )
        try:
            # Create new role permission
            new_permission = RolePermission(
                id=uuid4().hex,
                organization_role_id=new_role.id,
                permission_id=permission_id,
            )
            db.add(new_permission)
            db.commit()
            db.refresh(new_permission)
        except Exception as exc:
            raise CustomException(
                status_code=500,
                message="Failed to create new role permission",
                data={"role_id": new_role.id},
            ) from exc

        permissions.append(
            {
                "id": permission_id,
                "name": permission.name,
                "description": permission.description,
            }
        )

    return {
        "id": new_role.id,
        "name": new_role.name,
        "description": new_role.description,
        "permissions": permissions,
    }


def get_all_roles(db: Session, organization_id: str) -> List[Dict[str, Any]]:
    """Get all roles.

    Args:
        db (Session): Database session
        organization_id (str): Organization ID

    Raises:
        CustomException: If organization does not exist

    Returns:
        list: List of roles
    """
    # Check if organization ab746d6exists
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


def get_role_details(
    db: Session, organization_id: str, role_id: str
) -> Dict[str, Any]:
    """Get role details.

    Args:
        db (Session): Database session
        organization_id (str): Organization ID
        role_id (str): Role ID

    Raises:
        CustomException: If organization does not exist
        CustomException: If role does not exist

    Returns:
        dict: Role details
    """
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


class Role(BaseModel):  # type: ignore
    """Role Model.

    Attributes:
        name (str): Role name
        description (str): Role description
        organization_id (str): Organization ID
        permissions (Optional[PermissionManager]): Permission Manager
        is_default (bool): Is default role

    Raises:
        ValueError: If name is not provided
        ValueError: If description is not provided
        ValueError: If organization_id is not provided
    """

    name: str
    description: str
    organization_id: str
    permissions: Optional[PermissionManager]
    is_default: bool = False

    class Config:
        """Config for this model."""

        from_attributes = True

    def create_role(self, db: Session) -> Any:
        """Creates a new role.

        Args:
            db (Session): SQLAlchemy Session

        Returns:
            str: Role ID
        """

        if (
            self.get_role_by_name(
                db, self.name, organization_id=self.organization_id
            )
            is not None
        ):
            raise CustomException(
                status_code=400,
                message="Role with same name already exists",
                data={"role_name": self.name},
            )
        role_intance = OrganizationRole(
            id=uuid4().hex,
            name=self.name,
            description=self.description,
            organization_id=self.organization_id,
            is_default=self.is_default,
        )

        db.add(role_intance)
        db.commit()
        db.refresh(role_intance)

        self.assign_permissions(db, role_intance.id)

        return role_intance.id

    def assign_permissions(self, db: Session, role_id: str) -> bool:
        """Assigns all permissions to a role.

        Args:
            db (Session): SQLAlchemy Session
            role_id (str): Role ID

        Returns:
            bool: True if successful, False otherwise.
        """
        perm = PermissionManager.get_all_permissions(self, db)

        for permission in perm:
            role_permission = RolePermission(
                id=uuid4().hex,
                organization_role_id=role_id,
                permission_id=permission[0],
            )
            db.add(role_permission)
            db.commit()
            db.refresh(role_permission)

        return True

    def get_role(self, db: Session, role_id: str) -> Dict[str, Any]:
        """Gets a role by ID.

        Args:
            db (Session): SQLAlchemy Session
            role_id (str): Role ID

        Returns:
            Optional[OrganizationRole]: Role if found, None otherwise.
        """
        role = (
            db.query(OrganizationRole)
            .filter(OrganizationRole.id == role_id)
            .first()
        )
        return Role(
            name=role.name,
            description=role.description,
            organization_id=role.organization_id,
            permissions=PermissionManager.get_role_permissions(
                self, db, role_id
            ),
            is_default=role.is_default,
        )

    def get_role_by_name(
        self, db: Session, role_name: str, organization_id: str
    ) -> Any:
        """Gets a role by name.

        Args:
            db (Session): SQLAlchemy Session
            role_name (str): Role Name

        Returns:
            Optional[OrganizationRole]: Role if found, None otherwise.
        """
        role = (
            db.query(OrganizationRole)
            .filter(
                OrganizationRole.name == role_name,
                OrganizationRole.organization_id == organization_id,
            )
            .first()
        )
        if not role:
            return None
        return Role(
            name=role.name,
            description=role.description,
            organization_id=role.organization_id,
            permissions=PermissionManager.get_role_permissions(
                self, db, role.id
            ),
            is_default=role.is_default,
        )

    def get_all_organization_roles(
        self, db: Session, organization_id: str
    ) -> List[Dict[str, Any]]:
        """Gets all roles for an organization.

        Args:
            db (Session): SQLAlchemy Session
            organization_id (str): Organization ID

        Returns:
            List[OrganizationRole]: List of roles for an organization.
        """
        roles = (
            db.query(OrganizationRole)
            .filter(OrganizationRole.organization_id == organization_id)
            .all()
        )
        return [
            Role(
                name=role.name,
                description=role.description,
                organization_id=role.organization_id,
                permissions=PermissionManager.get_role_permissions(
                    self, db, role.id
                ),
                is_default=role.is_default,
            )
            for role in roles
        ]
