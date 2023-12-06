"""Role services."""
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from app.api.models.organization_models import (
    OrganizationMember,
    OrganizationRole,
)
from app.api.models.role_models import Role as RoleModel
from app.api.models.role_models import RolePermission
from app.database.connection import get_db_unyield
from app.services.permission_services import (
    APP_PERMISSION,
    PermissionManager,
    PermissionSchema,
)


class RoleService(BaseModel):  # type: ignore
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

    id: Optional[str] = None
    name: str = ""
    description: str = ""
    organization_id: str = ""
    is_super_admin: bool = False
    permissions: Optional[List[PermissionSchema]] = []
    is_default: bool = False

    class Config:
        """Config for this model."""

        from_attributes = True

    def get_default_role(self, db: Session, name: str) -> Any:
        """Gets the default role.

        Args:
            db (Session): SQLAlchemy Session

        Returns:
            Optional[OrganizationRole]: Role if found, None otherwise.
        """
        role = (
            db.query(RoleModel).filter_by(name=name, is_default=True).first()
        )
        return role

    def create_role(self, db: Session) -> Any:
        """Creates a new role.

        Args:
            db (Session): SQLAlchemy Session

        Returns:
            str: Role ID
        """
        # check if role already exists
        role = self.get_role_by_name(
            db, self.name, self.is_default, self.is_super_admin
        )

        if role is None:
            role = RoleModel(
                id=uuid4().hex,
                name=self.name,
                description=self.description,
                is_default=self.is_default,
                is_super_admin=self.is_super_admin,
            ).create_role(db)

        if self.organization_id != "":
            self.add_role_to_organization(db, self.organization_id, role.id)

        if self.permissions is not None:
            self.assign_permissions(db, role.id, self.permissions)
        else:
            print(f"Role {role.name} has no permissions")

        return role

    def add_role_to_organization(
        self, db: Session, organization_id: str, role_id: str
    ) -> Any:
        """Adds a role to an organization.

        Args:
            db (Session): SQLAlchemy Session
            organization_id (str): Organization ID
            role_id (str): Role ID
        Returns:
            str: Role ID
        """
        role_intance = OrganizationRole(
            id=uuid4().hex,
            organization_id=organization_id,
            role_id=role_id,
        )

        db.add(role_intance)
        db.commit()
        db.refresh(role_intance)

        return role_intance

    def assign_permissions(
        self,
        db: Session,
        role_id: str,
        permissions: List[PermissionSchema] | None,
    ) -> None:
        """Assigns permissions to a role.

        Args:
            db (Session): SQLAlchemy Session
            role_id (str): Role ID
            permissions (PermissionSchema): Permission Schema
        """
        #    bulk insert into role_permissions
        # check if role has permissions
        role_permissions = (
            db.query(RolePermission)
            .filter(RolePermission.role_id == role_id)
            .all()
        )
        if role_permissions is not None:
            db.query(RolePermission).filter(
                RolePermission.role_id == role_id
            ).delete()
            db.commit()
        perm_list = []
        perm_list = [
            {
                "id": uuid4().hex,
                "role_id": role_id,
                "permission_id": perm.id,
            }
            for perm in permissions
        ]

        db.bulk_insert_mappings(RolePermission, perm_list)
        db.commit()

    def update_role_permissions(
        self, db: Session, role_id: str
    ) -> Dict[str, Any]:
        """Updates role permissions.

        Args:
            db (Session): SQLAlchemy Session
            role_id (str): Role ID
            permissions (List): Permission Manager
        """
        # delete existing permissions
        db.query(RolePermission).filter(
            RolePermission.role_id == role_id
        ).delete()
        db.commit()

        # assign new permissions
        self.assign_permissions(db, role_id, self.permissions)

        return self.get_role(db, role_id)

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
            .filter(OrganizationRole.role_id == role_id)
            .first()
        )
        return {
            "id": role.role.id,
            "name": role.role.name,
            "description": role.role.description,
            "is_default": role.role.is_default,
            "is_super_admin": role.role.is_super_admin,
            "permissions": PermissionManager.get_role_permissions(
                self, db, role.role.id
            ),
        }

    def get_role_by_name(
        self,
        db: Session,
        role_name: str,
        is_default: bool = False,
        is_super_admin: bool = False,
    ) -> RoleModel:
        """Gets a role by name.

        Args:
            db (Session): SQLAlchemy Session
            role_name (str): Role name

        Returns:
            Optional[OrganizationRole]: Role if found, None otherwise.
        """

        role: RoleModel = (
            db.query(RoleModel)
            .filter(
                RoleModel.name == role_name,
                RoleModel.is_default == is_default,
                RoleModel.is_super_admin == is_super_admin,
            )
            .first()
        )
        return role

    def get_all_organization_roles(self, db: Session) -> List["RoleService"]:
        """Gets all roles for an organization.

        Args:
            db (Session): SQLAlchemy Session
            organization_id (str): Organization ID

        Returns:
            List[OrganizationRole]: List of roles for an organization.
        """
        roles_instance = (
            db.query(OrganizationRole)
            .filter(OrganizationRole.organization_id == self.organization_id)
            .all()
        )
        roles = []
        for role in roles_instance:
            roles.append(
                RoleService(
                    id=role.role.id,
                    name=role.role.name,
                    description=role.role.description,
                    is_default=role.role.is_default,
                    is_super_admin=role.role.is_super_admin,
                    permissions=PermissionManager.get_role_permissions(
                        self, db, role.role.id
                    ),
                ).model_dump()
            )
        return roles

    def assign_role(
        self,
        organization_id: str,
        organization_role_id: str,
        account_id: str,
        db: Session,
    ) -> None:
        """Assigns a role to a user.

        Args:
            organization_role_id (str): Organization Role ID
            user_id (str): User ID
        """

        # assign role to user
        member = OrganizationMember(
            id=uuid4().hex,
            organization_id=organization_id,
            account_id=account_id,
            organization_role_id=organization_role_id,
        )
        db.add(member)
        db.commit()
        db.refresh(member)


def create_default_roles(db: object = get_db_unyield) -> None:
    """Creates default roles for an organization.

    Args:
        db (Session): SQLAlchemy Session
        organization_id (str): Organization ID
        is_super_admin (bool, optional): Is super admin. Defaults to False.
    """
    # create default roles
    RoleService(
        name="Admin",
        description="Admin",
        is_default=True,
        is_super_admin=True,
        permissions=APP_PERMISSION.get_all_permissions(db)[1],
    ).create_role(db)

    # RoleService(
    #     name="Event Planner",
    #     description="Event Planner",
    #     is_default=True,
    #     is_super_admin=False,
    #     permissions=PermissionManager.
