"""This file contains the models for the tag table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class OrganizationTag(Base):  # type: ignore
    """
    OrganizationTag:
      This class is used to create the organization_tag table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      organization_id: This is the foreign key of the \
        organization table.
      title: This is the title of the organization tag.
      description: This is the description of the organization tag.
      created_at: This is the date and time when the organization \
        tag was created.
      updated_at: This is the date and time when the organization \
        tag was updated.

    Relationships:
      organization: This is the relationship between the organization \
        and organization_tag table.

    """

    __tablename__ = "organization_tag"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag = Column(String, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="organization_tag", lazy="joined"
    )
