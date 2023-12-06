"""This module contains all the schemas and classes related to permissions."""
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.models.permission_models import Permission
from app.api.models.role_models import RolePermission


class Plan(str, Enum):
    """Plan Enum.

    This enum defines the plans for the permissions.
    """

    BASIC = "basic"
    CORE = "core"
    PREMIUM = "premium"


class PermissionSchema(BaseModel):  # type: ignore
    """Base Permission Schema. It is used to create a new permission.

    Attributes:
        id (str): Permission ID
        permission_class (str): Permission Class
        name (str): Permission Name
        description (str): Permission Description
    """

    id: Optional[str] = None
    permission_class: str
    name: str
    plan: Plan = Plan.BASIC
    description: str

    class Config:
        """Pydantic Config Class."""

        from_attributes = True


class EventPerm(BaseModel):  # type: ignore
    """Event Permission Schema. This class defines all the permissions related
    to events.

    Attributes:
        create_event (PermissionSchema): Permission to create an event.
        read_event (PermissionSchema): Permission to read an event.
        update_event (PermissionSchema): Permission to update an event.
        update_event_website_status (PermissionSchema): Permission to update \
            event website status.
        update_event_website_layout (PermissionSchema): Permission to update \
            event website layout.
        delete_event (PermissionSchema): Permission to delete an event.
    """

    create_event: Optional[PermissionSchema] = None
    read_event: Optional[PermissionSchema] = None
    update_event: Optional[PermissionSchema] = None
    update_event_website_status: Optional[PermissionSchema] = None
    update_event_website_layout: Optional[PermissionSchema] = None
    delete_event: Optional[PermissionSchema] = None


class GuestPerm(BaseModel):  # type: ignore
    """Guest Permission Schema. This class defines all the permissions related
    to guests.

    Attributes:
        create_guest (PermissionSchema): Permission to create a guest.
        read_guest (PermissionSchema): Permission to read a guest.
        update_guest (PermissionSchema): Permission to update a guest.
        create_guest_import (PermissionSchema): Permission to import guest \
            list.
        create_guest_export (PermissionSchema): Permission to export guest \
            list.
    """

    create_guest: Optional[PermissionSchema] = None
    read_guest: Optional[PermissionSchema] = None
    update_guest: Optional[PermissionSchema] = None
    create_guest_import: Optional[PermissionSchema] = None
    create_guest_export: Optional[PermissionSchema] = None


class TaskPerm(BaseModel):  # type: ignore
    """Task Permission Schema. This class defines all the permissions related
    to tasks.

    Attributes:
        create_task (PermissionSchema): Permission to create a task.
        read_task (PermissionSchema): Permission to read a task.
        update_task (PermissionSchema): Permission to update a task.
        delete_task (PermissionSchema): Permission to delete a task.
    """

    create_task: Optional[PermissionSchema] = None
    read_task: Optional[PermissionSchema] = None
    update_task: Optional[PermissionSchema] = None
    delete_task: Optional[PermissionSchema] = None


class RolePerm(BaseModel):  # type: ignore
    """Role Permission Schema. This class defines all the permissions related
    to roles.

    Attributes:
        create_role (PermissionSchema): Permission to create a role.
        read_role (PermissionSchema): Permission to read a role.
        update_role (PermissionSchema): Permission to update a role.
        delete_role (PermissionSchema): Permission to delete a role.
    """

    create_role: Optional[PermissionSchema] = None
    read_role: Optional[PermissionSchema] = None
    update_role: Optional[PermissionSchema] = None
    delete_role: Optional[PermissionSchema] = None


class InvitationPerm(BaseModel):  # type: ignore
    """Invitation Permission Schema. This class defines all the permissions
    related to invitations.

    Attributes:
        create_invitation (PermissionSchema): Permission to create \
            an invitation.
        read_invitation (PermissionSchema): Permission to read an \
            invitation.
        update_invitation (PermissionSchema): Permission to update an \
            invitation.
        delete_invitation (PermissionSchema): Permission to delete an \
            invitation.
    """

    create_invitation: Optional[PermissionSchema] = None
    read_invitation: Optional[PermissionSchema] = None
    update_invitation: Optional[PermissionSchema] = None
    delete_invitation: Optional[PermissionSchema] = None


class MealPerm(BaseModel):  # type: ignore
    """Meal Permission Schema. This class defines all the permissions related
    to meals.

    Attributes:
        create_meal (PermissionSchema): Permission to create a meal.
        read_meal (PermissionSchema): Permission to read a meal.
        update_meal (PermissionSchema): Permission to update a meal.
        delete_meal (PermissionSchema): Permission to delete a meal.
        create_meal_tag (PermissionSchema): Permission to create a meal tag.
        read_meal_tag (PermissionSchema): Permission to read a meal tag.
        update_meal_tag (PermissionSchema): Permission to update a meal tag.
        delete_meal_tag (PermissionSchema): Permission to delete a meal tag.
        create_meal_category (PermissionSchema): Permission to create a \
            meal category.
        read_meal_category (PermissionSchema): Permission to read a meal \
            category.
        update_meal_category (PermissionSchema): Permission to update a \
            meal category.
        delete_meal_category (PermissionSchema): Permission to delete a \
            meal category.
    """

    create_meal: Optional[PermissionSchema] = None
    read_meal: Optional[PermissionSchema] = None
    update_meal: Optional[PermissionSchema] = None
    delete_meal: Optional[PermissionSchema] = None
    create_meal_tag: Optional[PermissionSchema] = None
    read_meal_tag: Optional[PermissionSchema] = None
    update_meal_tag: Optional[PermissionSchema] = None
    delete_meal_tag: Optional[PermissionSchema] = None
    create_meal_category: Optional[PermissionSchema] = None
    read_meal_category: Optional[PermissionSchema] = None
    update_meal_category: Optional[PermissionSchema] = None
    delete_meal_category: Optional[PermissionSchema] = None


class PermissionManager(BaseModel):  # type: ignore
    """Permission Manager Schema. This class defines all the permissions
    related to the application.

    Attributes:
        event (EventPerm): Event Permissions
        guest (GuestPerm): Guest Permissions
        task (TaskPerm): Task Permissions
        role (RolePerm): Role Permissions
        invitation (InvitationPerm): Invitation Permissions
        meal (MealPerm): Meal Permissions

    It also contains methods to get all permissions, get permissions by class,
    get permission by class and name, get role permissions, \
        and check if a role has a permission.

    Methods:
        get_all_permissions (db: Session): Get all permissions from database.
        get_permissions (db: Session, permission_class: str): Get all \
            permissions by class from database.
        get_permission (db: Session, permission_class: \
            str, permission_name: str): Get permission by class and \
                name from database.
        get_role_permissions (db: Session, role_id: str): Get all permissions \
            for a role from the database.
        is_permitted (db: Session, role_id: str, permission_class:List[str], \
            permission_name:List[str]): Check if a role has a permission.
    """

    event: Optional[EventPerm] | Dict[str, Any] = {}
    guest: Optional[GuestPerm] | Dict[str, Any] = {}
    task: Optional[TaskPerm] | Dict[str, Any] = {}
    role: Optional[RolePerm] | Dict[str, Any] = {}
    invitation: Optional[InvitationPerm] | Dict[str, Any] = {}
    meal: Optional[MealPerm] | Dict[str, Any] = {}

    def get_all_permissions(self, db: Session) -> List[PermissionSchema]:
        """Get all permissions from database.

        Args:
            db (Session): Database session.

        Returns:
            Dict[str, Permission]: Dict of permissions.
        """
        permissions_dict: Dict[str, Any] = {}
        permissions_list: List[PermissionSchema] = []
        permissions = db.query(Permission).all()

        for permission in permissions:
            permission_schema = PermissionSchema(
                id=permission.id,
                permission_class=permission.permission_class,
                name=permission.name,
                plan=permission.plan,
                description=permission.description,
            ).model_dump()
            if permission_schema not in permissions_list:
                permissions_list.append(permission_schema)
            if permission.permission_class in permissions_dict:
                permissions_dict[permission.permission_class].append(
                    permission_schema
                )
            else:
                permissions_dict[permission.permission_class] = [
                    permission_schema
                ]

        return permissions_dict, permissions_list

    def get_permissions(
        self, db: Session, permission_class: str
    ) -> Dict[str, Permission]:
        """Get all permissions by class from database.

        Args:
            db (Session): Database session.
            permission_class (str): Permission class.

        Returns:
            Dict[str, Permission]: Dict of permissions.
        """
        permissions = (
            db.query(Permission)
            .filter(Permission.permission_class == permission_class)
            .all()
        )
        return PermissionManager(
            **{
                permission.permission_class: permission
                for permission in permissions
            }
        )

    def get_permission(
        self, db: Session, permission_class: str, permission_name: str
    ) -> Any:
        """Get permission by class and name from database.

        Args:
            db (Session): Database session.
            permission_class (str): Permission class.
            permission_name (str): Permission name.

        Returns:
            Permission: Permission object.
        """
        permission = (
            db.query(Permission)
            .filter(
                Permission.permission_class == permission_class,
                Permission.name == permission_name,
            )
            .first()
        )
        return permission

    def get_role_permissions(
        self, db: Session, role_id: str
    ) -> List[PermissionSchema]:
        """Get all permissions for a role from the database.

        Args:
            db (Session): Database session.
            role_id (str): Role ID.

        Returns:
            Dict[str, Permission]: Dict of permissions.
        """
        role_perms = (
            db.query(RolePermission)
            .filter(RolePermission.role_id == role_id)
            .all()
        )

        return [
            PermissionSchema(
                id=role_perm.permission.id,
                permission_class=role_perm.permission.permission_class,
                name=role_perm.permission.name,
                plan=role_perm.permission.plan,
                description=role_perm.permission.description,
            ).model_dump()
            for role_perm in role_perms
        ]

    def is_permitted(
        self,
        db: Session,
        role_id: str,
        permission_class: List[str],
        permission_name: List[str],
    ) -> bool:
        """Check if a role has a permission.

        Args:
            db (Session): Database session.
            role_id (str): Role ID.
            permission_class (List[str]): Permission class.
            permission_name (List[str]): Permission name.

        Returns:
            bool: True if role has permission, else False.
        """
        role_permissions = (
            db.query(RolePermission)
            .filter(RolePermission.organization_role_id == role_id)
            .all()
        )
        for role_permission in role_permissions:
            if (
                role_permission.permission.permission_class in permission_class
                and role_permission.permission.name in permission_name
            ):
                return True
        return False

    def create_permissions(self, db: Session) -> None:
        """Create permissions in database.

        Args:
            db (Session): Database session.

        Returns:
            None
        """
        permissions_to_insert = []
        permissions_to_update = []
        for _, value in self:
            for _, v in value:
                permission = (
                    db.query(Permission)
                    .filter(
                        Permission.permission_class == v.permission_class,
                        Permission.name == v.name,
                    )
                    .first()
                )
                if permission:
                    # The permission already exists, so it needs to be updated
                    permissions_to_update.append(
                        {
                            "id": permission.id,
                            "permission_class": v.permission_class,
                            "name": v.name,
                            "description": v.description,
                            "plan": v.plan,
                        }
                    )
                else:
                    # The permission does not exist, so it needs to be inserted
                    permissions_to_insert.append(
                        {
                            "id": v.id,
                            "permission_class": v.permission_class,
                            "name": v.name,
                            "description": v.description,
                            "plan": v.plan,
                        }
                    )

        # Use bulk_insert_mappings and refresh to insert and update permissions
        print("updating existing permissions...")
        db.bulk_update_mappings(Permission, permissions_to_update)
        print("inserting new permissions...")
        db.bulk_insert_mappings(Permission, permissions_to_insert)

        # Refresh all permissions
        for _, value in self:
            for _, v in value:
                permission = (
                    db.query(Permission)
                    .filter(
                        Permission.permission_class == v.permission_class,
                        Permission.name == v.name,
                    )
                    .first()
                )
                if permission:
                    db.refresh(permission)

        db.commit()
        db.close()


APP_PERMISSION = PermissionManager(
    event=EventPerm(
        create_event=PermissionSchema(
            id=uuid4().hex,
            permission_class="event",
            name="create::event",
            plan="basic",
            description="Create an event.",
        ),
        read_event=PermissionSchema(
            id=uuid4().hex,
            permission_class="event",
            name="read::event",
            plan="basic",
            description="Read an event.",
        ),
        update_event=PermissionSchema(
            id=uuid4().hex,
            permission_class="event",
            name="update::event",
            plan="basic",
            description="Edit Event Name and Details",
        ),
        update_event_website_status=PermissionSchema(
            id=uuid4().hex,
            permission_class="event",
            name="update::event::website::status",
            plan="basic",
            description="Publish or Unpublish Event Website",
        ),
        update_event_website_layout=PermissionSchema(
            id=uuid4().hex,
            permission_class="event",
            name="update::event::website::layout",
            plan="basic",
            description="Customize Website Design and Layout",
        ),
        delete_event=PermissionSchema(
            id=uuid4().hex,
            permission_class="event",
            name="delete::event",
            plan="basic",
            description="Delete an event.",
        ),
    ),
    guest=GuestPerm(
        create_guest=PermissionSchema(
            id=uuid4().hex,
            permission_class="guest",
            name="create::guest",
            plan="basic",
            description="Create a guest.",
        ),
        read_guest=PermissionSchema(
            id=uuid4().hex,
            permission_class="guest",
            name="read::guest",
            plan="basic",
            description="Read a guest.",
        ),
        update_guest=PermissionSchema(
            id=uuid4().hex,
            permission_class="guest",
            name="update::guest",
            plan="basic",
            description="Update guests.",
        ),
        create_guest_import=PermissionSchema(
            id=uuid4().hex,
            permission_class="guest",
            name="create::guest::import",
            plan="basic",
            description="Import Guest List.",
        ),
        create_guest_export=PermissionSchema(
            id=uuid4().hex,
            permission_class="guest",
            name="create::guest::export",
            plan="basic",
            description="Export Guest List.",
        ),
    ),
    task=TaskPerm(
        create_task=PermissionSchema(
            id=uuid4().hex,
            permission_class="task",
            name="create::task",
            plan="basic",
            description="Create a task.",
        ),
        read_task=PermissionSchema(
            id=uuid4().hex,
            permission_class="task",
            name="read::task",
            plan="basic",
            description="Read a task.",
        ),
        update_task=PermissionSchema(
            id=uuid4().hex,
            permission_class="task",
            name="update::task",
            plan="basic",
            description="Update a task.",
        ),
        delete_task=PermissionSchema(
            id=uuid4().hex,
            permission_class="task",
            name="delete::task",
            plan="basic",
            description="Delete a task.",
        ),
    ),
    role=RolePerm(
        create_role=PermissionSchema(
            id=uuid4().hex,
            permission_class="role",
            name="create::role",
            plan="basic",
            description="Create a role.",
        ),
        read_role=PermissionSchema(
            id=uuid4().hex,
            permission_class="role",
            name="read::role",
            plan="basic",
            description="Read a role.",
        ),
        update_role=PermissionSchema(
            id=uuid4().hex,
            permission_class="role",
            name="update::role",
            plan="basic",
            description="Update a role.",
        ),
        delete_role=PermissionSchema(
            id=uuid4().hex,
            permission_class="role",
            name="delete::role",
            plan="basic",
            description="Delete a role.",
        ),
    ),
    invitation=InvitationPerm(
        create_invitation=PermissionSchema(
            id=uuid4().hex,
            permission_class="invitation",
            name="create::invitation",
            plan="basic",
            description="Create an invitation.",
        ),
        read_invitation=PermissionSchema(
            id=uuid4().hex,
            permission_class="invitation",
            name="read::invitation",
            plan="basic",
            description="Read an invitation.",
        ),
        update_invitation=PermissionSchema(
            id=uuid4().hex,
            permission_class="invitation",
            name="update::invitation",
            plan="basic",
            description="Update an invitation.",
        ),
        delete_invitation=PermissionSchema(
            id=uuid4().hex,
            permission_class="invitation",
            name="delete::invitation",
            plan="basic",
            description="Delete an invitation.",
        ),
    ),
    meal=MealPerm(
        create_meal=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="create::meal",
            plan="basic",
            description="Create a meal.",
        ),
        read_meal=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="read::meal",
            plan="basic",
            description="Read a meal.",
        ),
        update_meal=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="update::meal",
            plan="basic",
            description="Update a meal.",
        ),
        delete_meal=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="delete::meal",
            plan="basic",
            description="Delete a meal.",
        ),
        create_meal_tag=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="create::meal::tag",
            plan="basic",
            description="Create a meal tag.",
        ),
        read_meal_tag=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="read::meal::tag",
            plan="basic",
            description="Read a meal tag.",
        ),
        update_meal_tag=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="update::meal::tag",
            plan="basic",
            description="Update a meal tag.",
        ),
        delete_meal_tag=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="delete::meal::tag",
            plan="basic",
            description="Delete a meal tag.",
        ),
        create_meal_category=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="create::meal::category",
            plan="basic",
            description="Create a meal category.",
        ),
        read_meal_category=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="read::meal::category",
            plan="basic",
            description="Read a meal category.",
        ),
        update_meal_category=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="update::meal::category",
            plan="basic",
            description="Update a meal category.",
        ),
        delete_meal_category=PermissionSchema(
            id=uuid4().hex,
            permission_class="meal",
            name="delete::meal::category",
            plan="basic",
            description="Delete a meal category.",
        ),
    ),
)
