"""This file contains the models for the organization table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database.connection import Base

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
    id = Column(String, primary_key=True, default=uuid4().hex)
    name = Column(String, nullable=False)
    owner = Column(
        String, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    org_type = Column(ENUM("Wedding", name="event_type"), nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    account = relationship(
        "Account", back_populates="organizations", lazy="joined"
    )
    detail = relationship(
        "OrganizationDetail", back_populates="organization", lazy="joined"
    )
    organization_members = relationship(
        "OrganizationMember", back_populates="organization", lazy="joined"
    )
    organization_tag = relationship(
        "OrganizationTag", back_populates="organization", lazy="joined"
    )
    gifts = relationship("Gift", back_populates="organization", lazy="joined")
    budget = relationship(
        "Budget", back_populates="organization", lazy="joined"
    )
    meal_categories = relationship(
        "MealCategory", back_populates="organization", lazy="joined"
    )
    tags = relationship(
        "OrganizationTag", back_populates="organization", lazy="joined"
    )
    organization_roles = relationship(
        "OrganizationRole", back_populates="organization", lazy="joined"
    )
    organization_invite = relationship(
        "OrganizationInvite", back_populates="organization", lazy="joined"
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
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_location = Column(
        String,
    )
    website = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    event_start_time = Column(
        DateTime,
    )
    event_end_time = Column(
        DateTime,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", back_populates="detail", lazy="joined"
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
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id = Column(
        String, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    organization_role_id = Column(
        String,
        ForeignKey("organization_role.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_suspended = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="organization_member", lazy="joined"
    )
    account = relationship("Account", backref="member_account", lazy="joined")
    member_role = relationship(
        "OrganizationRole", back_populates="members", lazy="joined"
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
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id = Column(String, ForeignKey("role.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", back_populates="organization_roles", lazy="joined"
    )
    role = relationship("Role", backref="organization_role", lazy="joined")
    members = relationship(
        "OrganizationMember", back_populates="member_role", lazy="joined"
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
    account_id = Column(
        String, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_member_id = Column(
        String, ForeignKey("organization_member.id"), nullable=True
    )
    token = Column(String, nullable=False)
    time_sent = Column(DateTime, default=datetime.utcnow)
    time_accepted_or_rejected = Column(DateTime, nullable=True)
    status = Column(
        ENUM("pending", "accepted", "rejected", name="invitation_status"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    account = relationship(
        "Account", backref="organization_invite", lazy="joined"
    )
    organization = relationship(
        "Organization", back_populates="organization_invite", lazy="joined"
    )


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
    name = Column(String, nullable=False)
    tag_type = Column(
        ENUM("dietary", "guest", name="tag_type"), nullable=False
    )
    description = Column(
        String,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", back_populates="organization_tag", lazy="joined"
    )
    meal_tags = relationship(
        "MealTag", back_populates="organization_tag", lazy="joined"
    )
