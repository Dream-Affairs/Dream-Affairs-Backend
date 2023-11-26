"""This file contains the models for the organization table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.api.models.account_models import Account, Auth  # noqa: F401
from app.api.models.budget_expenditure_models import (  # noqa: F401
    Budget,
    Expenditure,
)
from app.api.models.email_models import TrackEmail  # noqa: F401
from app.api.models.gift_models import (  # noqa: F401
    BankDetail,
    Gift,
    LinkDetail,
    PaymentOption,
    WalletDetail,
)
from app.api.models.meal_models import (  # noqa: F401
    Meal,
    MealCategory,
    MealTag,
)
from app.api.models.role_permission_models import (  # noqa: F401
    Permission,
    RolePermission,
)
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
    gifts = relationship(
        "Gift",
        back_populates="organization",
    )
    detail = relationship(
        "OrganizationDetail", back_populates="organization", lazy="joined"
    )
    organization_members = relationship(
        "OrganizationMember",
        back_populates="organization",
    )
    budget = relationship(
        "Budget",
        back_populates="organization",
    )
    meal_categories = relationship(
        "MealCategory",
        back_populates="organization",
    )
    tags = relationship(
        "OrganizationTag",
        back_populates="organization",
    )
    organization_roles = relationship(
        "OrganizationRole",
        back_populates="organization",
    )
    checklist = relationship(
        "Checklist",
        back_populates="organization",
    )

    bank_details = relationship(
        "BankDetail", back_populates="organization", lazy="joined"
    )
    link_details = relationship(
        "LinkDetail", back_populates="organization", lazy="joined"
    )
    wallet_details = relationship(
        "WalletDetail", back_populates="organization", lazy="joined"
    )
    track_email = relationship("TrackEmail", back_populates="organization")


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
    event_date = Column(DateTime)
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
      organization_role_id: This is the foreign key of the \
        organization_role table.
      invite_token: This is the token which is used to invite the \
        organization member.
      is_accepted: This is the boolean value which tells whether the \
        member is accepted or not.
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
      member_role: This is the relationship between the organization_role \
        and organization_member table.
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
    invite_token = Column(
        String,
    )
    is_accepted = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", back_populates="organization_members", lazy="joined"
    )
    account = relationship("Account", backref="member_account", lazy="joined")
    member_role = relationship(
        "OrganizationRole", back_populates="members", lazy="joined"
    )
    created_checklist = relationship(
        "Checklist",
        back_populates="created_by_member",
        foreign_keys="Checklist.created_by",
    )
    assigned_checklist = relationship(
        "Checklist",
        back_populates="assigned_to_member",
        foreign_keys="Checklist.assigned_to",
    )


class OrganizationRole(Base):  # type: ignore
    """
    OrganizationRole:
      This class is used to create the organization_role table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      name: This is the name of the organization role.
      description: This is the description of the organization role.
      organization_id: This is the foreign key of the organization tsble.
      is_default: This is the boolean value which tells whether the \
        organization role is default or not.
      created_at: This is the date and time when the organization\
         role was created.
      updated_at: This is the date and time when the organization\
         role was updated.

    Relationships:
      organization: This is the relationship between the organization \
        and organization_role table.
      members: This is the relationship between the organization_role \
        and organization_member table.
    """

    __tablename__ = "organization_role"
    id = Column(String, primary_key=True, default=uuid4().hex)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization",
        back_populates="organization_roles",
    )
    members = relationship(
        "OrganizationMember",
        back_populates="member_role",
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
        "Organization", back_populates="tags", lazy="joined"
    )
    meal_tags = relationship(
        "MealTag",
        back_populates="organization_tag",
    )


class Checklist(Base):  # type: ignore
    """
    Checklist model:
      This table contains the checklist for the organization.

    Attributes:
      id (str): The id of the checklist.
      organization_id (str): The id of the organization to which \
        the checklist belongs.
      title (str): The title of the checklist.
      description (str): The description of the checklist.
      status (str): The status of the checklist.
      is_completed (bool): The flag to indicate if the checklist is \
        completed.
      is_hidden (bool): The flag to indicate if the checklist is hidden.
      completed_at (datetime): The date and time when the checklist was \
        completed.
      created_at (datetime): The date and time when the checklist was \
        created.
      updated_at (datetime): The date and time when the checklist was \
        last updated.

      organization (object): The organization to which the checklist \
        belongs.

    """

    __tablename__ = "checklist"
    id = Column(String, primary_key=True, default=uuid4().hex)
    created_by = Column(
        String,
        ForeignKey("organization_member.id", ondelete="CASCADE"),
        nullable=False,
    )
    assigned_to = Column(
        String,
        ForeignKey("organization_member.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    description = Column(
        String,
    )
    status = Column(
        ENUM("completed", "pending", "overdue", name="checklist_status"),
        nullable=False,
    )
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    created_by_member = relationship(
        "OrganizationMember",
        back_populates="created_checklist",
        foreign_keys=[created_by],
        lazy="joined",
    )
    assigned_to_member = relationship(
        "OrganizationMember",
        back_populates="assigned_checklist",
        foreign_keys=[assigned_to],
        lazy="joined",
    )
    organization = relationship("Organization", back_populates="checklist")
