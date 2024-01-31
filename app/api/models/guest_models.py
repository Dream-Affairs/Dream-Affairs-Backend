"""Guest Models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Guest(Base):
    """
  Guest Model:
    This table contains the guests for the wedding.
    It allows the user to add guests, their plus ones, and \
      their table numbers and everything else.

  Attributes:
    id (str): The id of the guest.
    first_name (str): The first name of the guest.
    last_name (str): The last name of the guest.
    email (str): The email of the guest.
    phone_number (str): The phone number of the guest.
    organization_id (str): The id of the organization.
    rsvp_status (str): The status of the guest's RSVP.

    created_at (datetime): The date and time when the guest was \
      created.
    updated_at (datetime): The date and time when the guest was \
      last updated.

    Relationships:
      guest_plus_one: The relationship between the guest and \
        their plus one.
      guest_invite: The relationship between the guest and \
        their invite code.
      guest_tags: The relationship between the guest and \
        their tags.
      guest_table: The relationship between the guest and \
        their table.
  """

    __tablename__ = "guest"
    id = Column(String, primary_key=True, default=uuid4().hex)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False, default="")
    email = Column(String, nullable=False)
    phone_number = Column(String, default="")
    location = Column(String, default="")

    organization_id = Column(String, ForeignKey("organization.id"))
    rsvp_status = Column(
        ENUM("accepted", "declined", "pending", name="rsvp_status"),
        default="pending",
    )
    invite_code = Column(String, default="")

    allow_plus_one = Column(Boolean, default=False)
    has_plus_one = Column(Boolean, default=False)
    is_plus_one = Column(Boolean, default=False)
    plus_one_id = Column(String, ForeignKey("guest.id"))

    table_group = Column(String, ForeignKey("table_group.id"))
    table_number = Column(Integer, default=0)
    seat_number = Column(Integer, default=0)

    meal_id = Column(String, ForeignKey("meal.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    plus_one = relationship(
        "Guest", backref="guest_plus_one", remote_side=[id], lazy="joined"
    )
    guest_tags = relationship(
        "GuestTags", back_populates="guest", lazy="joined"
    )
    group = relationship(
        "OrganizationTable", back_populates="guests", lazy="joined"
    )
    organization = relationship(
        "Organization", backref="guests", lazy="joined"
    )
    meal = relationship("Meal", backref="guests", lazy="joined")


class GuestTags(Base):
    """
  Guest Tags Model:
    This table contains the guest tags for the wedding.
    It is used to keep track of tags for each guest.

  Attributes:
    guest_id (str): The id of the guest.
    tag_id (str): The id of the tag.

  Relationships:
    guest: The relationship between the guest and \
      their tags.
    tag: The relationship between the tag and \
      their guests.
  """

    __tablename__ = "guest_tags"

    id = Column(String, primary_key=True, default=uuid4().hex)
    guest_id = Column(
        String,
        ForeignKey("guest.id"),
    )
    tag_id = Column(String, ForeignKey("organization_tag.id"))

    guest = relationship("Guest", back_populates="guest_tags")
    organization_tag = relationship(
        "OrganizationTag", back_populates="guest_tags"
    )
