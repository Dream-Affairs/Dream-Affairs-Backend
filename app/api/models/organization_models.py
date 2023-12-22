"""This file contains the models for the organization table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.api.models.account_models import Account, Auth  # noqa: F401
from app.api.models.budget_expenditure_models import (  # noqa: F401
    Budget,
    Expenditure,
)
from app.api.models.gift_models import (  # noqa: F401
    BankDetail,
    Gift,
    LinkDetail,
    PaymentOption,
    WalletDetail,
)

# from app.api.models.guest_models import (  # noqa: F401
#     Guest,
#     Guest_Plus_One,
#     Guest_Table,
#     GuestTags,
# )
from app.api.models.meal_models import (  # noqa: F401
    Meal,
    MealCategory,
    MealTag,
)
from app.api.models.notification_models import TrackEmail  # noqa: F401
from app.api.models.permission_models import Permission  # noqa: F401

# from app.api.models.plan_models import OrganizationPlan, Plan  # noqa: F401
from app.api.models.role_models import Role, RolePermission  # noqa: F401
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
    description = Column(Text)
    logo = Column(String)
    plan = Column(
        ENUM("basic", "core", "premium", name="organization_plan"),
        nullable=False,
        default="basic",
    )
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    account = relationship(
        "Account",
        back_populates="organizations",
        lazy="joined",
        cascade="all,delete",
    )
    gifts = relationship(
        "Gift", back_populates="organization", cascade="all,delete"
    )
    detail = relationship(
        "OrganizationDetail",
        back_populates="organization",
        lazy="joined",
        cascade="all,delete",
        uselist=False,
    )
    organization_members = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all,delete",
    )
    budget = relationship(
        "Budget", back_populates="organization", cascade="all,delete"
    )
    meal_categories = relationship(
        "MealCategory", back_populates="organization", cascade="all,delete"
    )
    tags = relationship(
        "OrganizationTag", back_populates="organization", cascade="all,delete"
    )
    organization_roles = relationship(
        "OrganizationRole", back_populates="organization", cascade="all,delete"
    )
    checklist = relationship(
        "Checklist", back_populates="organization", cascade="all,delete"
    )

    bank_details = relationship(
        "BankDetail",
        back_populates="organization",
        lazy="joined",
        cascade="all,delete",
    )
    link_details = relationship(
        "LinkDetail",
        back_populates="organization",
        lazy="joined",
        cascade="all,delete",
    )
    wallet_details = relationship(
        "WalletDetail",
        back_populates="organization",
        lazy="joined",
        cascade="all,delete",
    )
    track_email = relationship(
        "TrackEmail", back_populates="organization", cascade="all,delete"
    )
    organization_invite = relationship(
        "InviteMember",
        back_populates="organization",
        lazy="joined",
        cascade="all,delete",
        uselist=False,
    )
    # plan = relationship(
    #     "OrganizationPlan",
    #     back_populates="organization",
    #     lazy="joined",
    #     cascade="all,delete",
    # )
    # tables = relationship(
    #     "OrganizationTable",
    #     back_populates="organization",
    #     cascade="all,delete",
    # )


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
    shipment_name = Column(String)
    shipment_primary_address = Column(String)
    shipment_secondary_address = Column(String)
    shipment_city = Column(String)
    shipment_state = Column(String)
    shipment_zip_code = Column(String)
    shipment_country = Column(String)
    shipment_phone_number = Column(String)

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
    invite_id = Column(
        String, ForeignKey("invite_member.id", ondelete="CASCADE")
    )
    is_suspended = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", back_populates="organization_members", lazy="joined"
    )
    account = relationship("Account", backref="member_account", lazy="joined")
    member_role = relationship(
        "OrganizationRole",
        back_populates="members",
        lazy="joined",
        cascade="all,delete",
    )
    created_checklist = relationship(
        "Checklist",
        back_populates="created_by_member",
        foreign_keys="Checklist.created_by",
        cascade="all,delete",
    )
    assigned_checklist = relationship(
        "Checklist",
        back_populates="assigned_to_member",
        foreign_keys="Checklist.assigned_to",
    )
    invite = relationship(
        "InviteMember",
        back_populates="member",
        foreign_keys=[invite_id],
        cascade="all,delete",
    )


class InviteMember(Base):  # type: ignore
    """
    InviteMember:

      This class is used to create the invite_member table.

    Args:
      Base: This is the base class from which all the models inherit.

    Attributes:
      id: This is the primary key of the table.
      organization_id: This is the foreign key of the organization table.
      account_id: This is the foreign key of the account table.
      invite_token: This is the token which is used to invite the \
        organization member.
      status: This is the status of the invite.
      is_accepted: This is the boolean value which tells whether the \
        member is accepted or not.
      sent_invite_date: This is the date and time when the invite was sent.
      accepted_invite_date: This is the date and time when the invite was \
        accepted.
      rejected_invite_date: This is the date and time when the invite was \
        rejected.
      created_at: This is the date and time when the invite was created.
      updated_at: This is the date and time when the invite was updated.
    """

    __tablename__ = "invite_member"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id = Column(
        String, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    invite_token = Column(String, nullable=False)
    status = Column(INVITE_STATUS, default="pending")
    is_accepted = Column(Boolean, default=False)
    sent_invite_date = Column(DateTime)
    accepted_invite_date = Column(DateTime)
    rejected_invite_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization",
        back_populates="organization_invite",
        uselist=False,
        cascade="all,delete",
    )
    account = relationship(
        "Account",
        backref="invite_account",
        lazy="joined",
        cascade="all,delete",
    )
    member = relationship(
        "OrganizationMember",
        back_populates="invite",
        lazy="joined",
        cascade="all,delete",
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
      organization_id: This is the foreign key of the organization table.
      role_id: This is the foreign key of the role table.
      is_default: This is the boolean value which tells whether the \
        role is default or not.
      created_at: This is the date and time when the organization role \
        was created.
      updated_at: This is the date and time when the organization role \
        was updated.

    Relationships:
      organization: This is the relationship between the organization and \
        organization_role table.
      members: This is the relationship between the organization_role and \
        organization_member table.
    """

    __tablename__ = "organization_role"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id = Column(
        String,
        ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False,
    )

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
    role = relationship("Role", backref="organization_role", lazy="joined")


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
        "MealTag", back_populates="organization_tag", cascade="all,delete"
    )
    # guest_tags = relationship(
    #     "GuestTags", back_populates="organization_tag", cascade="all,delete"
    # )


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
