"""This file contains the models for the gift table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Gift(Base):  # type: ignore
    """
    Gift model:
      This table contains the gift for the organization.

    Attributes:
      id (str): The id of the gift.
      organization_id (str): The id of the organization \
        to which the gift belongs.
      tile (str): The title of the gift.
      description (str): The description of the gift.
      product_unit_price (float): The unit price of the product.
      product_total_amount (float): The total amount of the product.
      product_quantity (int): The quantity of the product.
      product_url (str): The url of the product.
      product_image_url (str): The image url of the product.
      currency (str): The currency of the gift.
      payment_provider (str): The payment provider of the gift.
      payment_link (str): The payment link of the gift.
      gift_type (str): The type of the gift.
      gift_amount_type (str): The amount type of the gift.
      gift_status (str): The status of the gift.
      is_gift_hidden (bool): The flag to indicate if the gift is hidden.
      is_gift_amount_hidden (bool): The flag to indicate if the gift \
        amount is hidden.

      created_at (datetime): The date and time when the gift was created.
      updated_at (datetime): The date and time when the gift was last updated.
      deleted_at (datetime): The date and time when the gift was deleted.

      organization (object): The organization to which the gift belongs.
    """

    __tablename__ = "gift"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    description = Column(
        String,
    )
    product_unit_price = Column(
        Float(2),
    )
    product_total_amount = Column(
        Float(2),
    )
    product_quantity = Column(
        Integer,
    )
    product_url = Column(
        String,
    )
    product_image_url = Column(
        String,
    )
    currency = Column(
        String,
    )
    payment_provider = Column(
        String,
    )
    payment_link = Column(
        String,
    )
    bank_name = Column(
        String,
    )
    bank_account_number = Column(
        Integer,
    )
    bank_account_name = Column(
        String,
    )
    gift_type = Column(
        ENUM("physical", "cash", name="gift_type"), nullable=False
    )
    gift_amount_type = Column(
        ENUM("fixed", "any", name="gift_amount_type"),
        nullable=False,
        default="fixed",
    )
    gift_status = Column(
        ENUM("available", "reserved", "purchased", name="gift_status"),
        nullable=False,
        default="available",
    )
    is_gift_hidden = Column(Boolean, default=False)
    is_gift_amount_hidden = Column(Boolean, default=False)

    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    organization = relationship(
        "Organization", backref="associated_Organization", lazy="joined"
    )
