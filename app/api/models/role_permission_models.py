"""This file contains the models for the role and permission tables."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


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
    id = Column(String, primary_key=True, default=uuid4().hex)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)


class RolePermission(Base):  # type: ignore
    """
    RolePermission model:
      This table contains the relationship between the roles and permissions.

    Attributes:
      id (str): The id of the role permission.
      role_id (str): The id of the role.
      permission_id (str): The id of the permission.

      created_at (datetime): The date and time when the role permission \
        was created.
      updated_at (datetime): The date and time when the role permission \
        was last updated.

      role (Role): The role associated with the role permission.
      permission (Permission): The permission associated with the \
        role permission.
    """

    __tablename__ = "role_permission"
    id = Column(String, primary_key=True)
    organization_role_id = Column(
        String,
        ForeignKey("organization_role.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id = Column(
        String, ForeignKey("permission.id", ondelete="CASCADE"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    permission = relationship(
        "Permission", backref="role_permission", lazy=True
    )
