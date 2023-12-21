"""This file contains the models for the role and permission tables."""
from uuid import uuid4

from sqlalchemy import Column, String
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
    permission_class = Column(String, nullable=False)
    description = Column(String, nullable=False)

    role_permission = relationship(
        "RolePermission", back_populates="permission", cascade="all,delete"
    )
