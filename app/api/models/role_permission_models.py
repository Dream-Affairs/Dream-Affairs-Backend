"""This file contains the models for the role and permission tables."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Role(Base):  # type: ignore
    """
    Role model:
      This table contains the roles for the users. They are created \
        by organization owners.

    Attributes:
      id (str): The id of the role.
      name (str): The name of the role.
      description (str): The description of the role.
      is_deleted (bool): The flag to indicate if the role has been deleted.

      created_at (datetime): The date and time when the role was created.
      updated_at (datetime): The date and time when the role was last updated.
      deleted_at (datetime): The date and time when the role was deleted.

      permissions (list): The list of permissions associated with the role.
    """

    __tablename__ = "role"
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    permissions = relationship(
        "Permission",
        secondary="role_permission",
        lazy="subquery",
        backref="role",
    )


class Permission(Base):  # type: ignore
    """
    Permission model:
      This table contains the permissions for the users. \
        They are created by organization owners.

    Attributes:
      id (str): The id of the permission.
      name (str): The name of the permission.
      description (str): The description of the permission.
      is_deleted (bool): The flag to indicate if the permission has \
        been deleted.

      created_at (datetime): The date and time when the permission was \
        created.
      updated_at (datetime): The date and time when the permission was \
        last updated.
      deleted_at (datetime): The date and time when the permission \
        was deleted.

    """

    __tablename__ = "permission"
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


class RolePermission(Base):  # type: ignore
    """
    RolePermission model:
      This table contains the relationship between the roles and permissions.

    Attributes:
      id (str): The id of the role permission.
      role_id (str): The id of the role.
      permission_id (str): The id of the permission.
      is_deleted (bool): The flag to indicate if the role permission \
        has been deleted.

      created_at (datetime): The date and time when the role permission \
        was created.
      updated_at (datetime): The date and time when the role permission \
        was last updated.
      deleted_at (datetime): The date and time when the role permission \
        was deleted.

      role (Role): The role associated with the role permission.
      permission (Permission): The permission associated with the \
        role permission.
    """

    __tablename__ = "role_permission"
    id = Column(String, primary_key=True, default=uuid4)
    role_id = Column(String, ForeignKey("role.id"), nullable=False)
    permission_id = Column(String, ForeignKey("permission.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    role = relationship("Role", backref="role_permission", lazy=True)
    permission = relationship(
        "Permission", backref="role_permission", lazy=True
    )
