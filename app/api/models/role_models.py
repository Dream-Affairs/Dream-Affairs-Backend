"""This file contains the models for the role and permission tables."""
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Session, relationship

from app.database.connection import Base


class Role(Base):  # type: ignore
    """
    Role model:
    This table contains the roles for the users. \
        They are created by organization owners.

    Attributes:
    id (str): The id of the role.
    name (str): The name of the role.
    description (str): The description of the role.
    plan_type (str): The plan type of the role.
    is_deleted (bool): The flag to indicate if the role has been deleted.

    created_at (datetime): The date and time when the role was created.
    updated_at (datetime): The date and time when the role was last updated.
    deleted_at (datetime): The date and time when the role was deleted.

    role_permission (RolePermission): The role permission associated with \
        the role.
    """

    __tablename__ = "role"
    id = Column(String, primary_key=True, default=uuid4().hex)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_super_admin = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    role_permission = relationship(
        "RolePermission",
        back_populates="role",
    )

    def create_role(self, db: Session) -> "Role":
        """Create a new role."""
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def get_role_by_id(self, db: Session, role_id: str) -> Any:
        """Get a role by id."""
        return db.query(Role).filter(Role.id == role_id).first()


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
    id = Column(String, primary_key=True, default=uuid4().hex)
    role_id = Column(
        String,
        ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id = Column(
        String, ForeignKey("permission.id", ondelete="CASCADE"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    permission = relationship(
        "Permission", back_populates="role_permission", lazy="joined"
    )
    role = relationship(
        "Role", back_populates="role_permission", lazy="joined"
    )
