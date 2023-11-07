"""This file contains the models for the organization table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database.connection import Base

EVENT_TYPE = ENUM("Wedding", name="event_type")
INVITE_STATUS = ENUM("pending", "accepted", "rejected", name="invite_status")


class Organization(Base):  # type: ignore
    """
    Organization:
        This class is used to create the organization table.

    Args:
        Base: This is the base class from which all the models inherit.

    attributes:
        id: This is the primary key of the table.
        name: This is the name of the organization.
        owner: This is the owner of the organization.
        org_type: This is the type of the organization.
        is_deleted: This is the boolean value which tells whether \
          the organization is deleted or not.
        created_at: This is the date and time when the organization \
          was created.
        updated_at: This is the date and time when the organization \
          was updated.
        deleted_at: This is the date and time when the organization \
          was deleted.

    Relationships:

        account: This is the relationship between the organization \
          and account table.
        organization_detail: This is the relationship between the \
          organization and organization_detail table.
        organization_members: This is the relationship between the \
          organization and organization_member table.
        organization_invite: This is the relationship between the \
          organization and organization_invite table.
        organization_role: This is the relationship between the \
          organization and organization_role table.
        organization_tag: This is the relationship between the \
          organization and organization_tag table.
        gifts: This is the relationship between the organization \
          and gift table.
        budget: This is the relationship between the organization \
          and organization_budget table.


    """

    __tablename__ = "organization"
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    owner = Column(String, ForeignKey("account.id"), nullable=False)
    org_type = Column(EVENT_TYPE, nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    account = relationship("Account", backref="organization", lazy=True)
    detail = relationship(
        "OrganizationDetail", backref="organization", lazy=True
    )
    organization_members = relationship(
        "OrganizationMember", back_populates="organization", lazy=True
    )
    tag = relationship(
        "OrganizationTag", back_populates="organization", lazy=True
    )
    gifts = relationship("Gift", backref="organization", lazy=True)
    budget = relationship(
        "OrganizationBudget", backref="organization", lazy=True
    )
    meal_category = relationship(
        "MealCategory", backref="organization", lazy=True
    )


class OrganizationDetail(Base):  # type: ignore
    """
    OrganizationDetail:
      This class is used to create the organization_detail\
         table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      organization_id: This is the foreign key of the organization \
        table.
      event_location: This is the location of the event.
      website: This is the website of the organization.
      event_date: This is the date of the event.
      event_start_time: This is the start time of the event.
      event_end_time: This is the end time of the event.
      created_at: This is the date and time when the organization detail \
        was created.
      updated_at: This is the date and time when the organization detail \
        was updated.

    Relationships:
      organization: This is the relationship between the organization and \
        organization_detail table.
    """

    __tablename__ = "organization_detail"
    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        String, ForeignKey("organization.id"), nullable=False
    )
    event_location = Column(
        String,
    )
    website = Column(
        String,
    )
    event_date = Column(
        DateTime,
    )
    event_start_time = Column(
        DateTime,
    )
    event_end_time = Column(
        DateTime,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="organization_detail", lazy=True
    )


class OrganizationMember(Base):  # type: ignore
    """
    OrganizationMember:
      This class is used to create the organization_member table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      organization_id: This is the foreign key of the organization table.
      account_id: This is the foreign key of the account table.
      role_id: This is the foreign key of the role table.
      is_suspended: This is the boolean value which tells whether the \
        member is suspended or not.
      created_at: This is the date and time when the organization \
        member was created.
      updated_at: This is the date and time when the organization \
        member was updated.

    Relationships:
      organization: This is the relationship between the organization and \
        organization_member table.
      account: This is the relationship between the account and \
        organization_member table.
      role: This is the relationship between the role and \
        organization_member table.
    """

    __tablename__ = "organization_member"
    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        String, ForeignKey("organization.id"), nullable=False
    )
    account_id = Column(String, ForeignKey("account.id"), nullable=False)
    role_id = Column(
        String, ForeignKey("organization_role.id"), nullable=False
    )

    is_suspended = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="organization_member", lazy=True
    )
    account = relationship("Account", backref="organization_member", lazy=True)
    role = relationship(
        "Role",
        secondary="organization_role",
        lazy="subquery",
        backref="organization_member",
    )


class OrganizationInvite(Base):  # type: ignore
    """
    OrganizationInvite:
      This class is used to create the organization_invite table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      account_id: This is the foreign key of the account table.
      organization_id: This is the foreign key of the organization table.
      role_id: This is the foreign key of the role table.
      token: This is the token of the organization invite.
      time_sent: This is the date and time when the organization invite \
        was sent.
      time_accepted_or_rejected: This is the date and time when the \
        organization invite was accepted or rejected.
      status: This is the status of the organization invite.

    Relationships:
      account: This is the relationship between the account and \
        organization_invite table.
      organization: This is the relationship between the organization \
        and organization_invite table.
      role: This is the relationship between the role and \
        organization_invite table.
    """

    __tablename__ = "organization_invite"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey("account.id"), nullable=False)
    organization_id = Column(
        String, ForeignKey("organization.id"), nullable=False
    )
    role_id = Column(
        String, ForeignKey("organization_role.id"), nullable=False
    )
    token = Column(String, nullable=False)
    time_sent = Column(DateTime, default=datetime.utcnow)
    time_accepted_or_rejected = Column(DateTime, nullable=True)
    status = Column(INVITE_STATUS, nullable=False, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", backref="organization_invite", lazy=True)
    organization = relationship(
        "Organization", backref="organization_invite", lazy=True
    )
    role = relationship(
        "OrganizationRole", backref="organization_invite", lazy=True
    )


class OrganizationRole(Base):  # type: ignore
    """
    OrganizationRole:
      This class is used to create the organization_role table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      organization_id: This is the foreign key of the organization \
        table.
      role_id: This is the foreign key of the role table.
      created_at: This is the date and time when the organization\
         role was created.
      updated_at: This is the date and time when the organization\
         role was updated.

    Relationships:
      organization: This is the relationship between the organization \
        and organization_role table.
      role: This is the relationship between the role and \
        organization_role table.
    """

    __tablename__ = "organization_role"
    id = Column(String, primary_key=True, default=uuid4)
    organization_id = Column(
        String, ForeignKey("organization.id"), nullable=False
    )
    role_id = Column(String, ForeignKey("role.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="organization_role", lazy=True
    )
    role = relationship("Role", backref="organization_role", lazy=True)


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
    id = Column(String, primary_key=True, default=uuid4)
    organization_id = Column(
        String, ForeignKey("organization.id"), nullable=False
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="organization_tag", lazy=True
    )
