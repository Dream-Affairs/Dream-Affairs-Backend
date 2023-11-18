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
        "Organization", back_populates="gifts", lazy="joined"
    )
    payment_options = relationship(
        "PaymentOption", back_populates="gift", lazy="joined"
    )


class PaymentOption(Base):  # type: ignore
    """
    Payment option model:

    Attributes:
        id (str): The id of the payment option.
        payment_type (str): The type of the payment option.
        gift_id (str): The id of the gift to which the payment option belongs.
        payment_option_id (str): The id of the payment option.
        bank (object): The bank details of the payment option.
        wallet (object): The wallet details of the payment option.
        payment_link (object): The payment link details of the payment option.
        gift (object): The gift to which the payment option belongs.

    relationship:
        bank (object): The bank details of the payment option.
        wallet (object): The wallet details of the payment option.
        payment_link (object): The payment link details of the payment option.
        gift (object): The gift to which the payment option belongs.
    """

    __tablename__ = "payment_option"
    id = Column(String, primary_key=True, default=uuid4().hex)
    payment_type = Column(
        ENUM("bank", "wallet", "link", name="payment_type"),
        nullable=False,
    )
    gift_id = Column(
        String,
        ForeignKey("gift.id", ondelete="CASCADE"),
        nullable=False,
    )
    payment_option_id = Column(String, nullable=False)

    gift = relationship(
        "Gift", back_populates="payment_options", lazy="joined"
    )


class BankDetail(Base):  # type: ignore
    """
    Bank detail model:

    Attributes:
        id (str): The id of the bank detail.
        organization_id (str): The id of the organization to which the bank \
            detail belongs.
        name (str): The name of the bank.
        account_name (str): The name of the account.
        account_number (str): The account number.

    relationship:
        payment_options (object): The payment options to which the bank \
            detail belongs.
    """

    __tablename__ = "bank_detail"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)  # bank name
    account_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)

    payment_options = relationship(
        "PaymentOption", back_populates="bank", lazy="joined"
    )


class WalletDetail(Base):  # type: ignore
    """
    Wallet detail model:

    Attributes:
        id (str): The id of the wallet detail.
        organization_id (str): The id of the organization to which the \
            wallet detail belongs.
        name (str): The name of the wallet.
        wallet_tag (str): The tag of the wallet.

    relationship:
        payment_options (object): The payment options to which the wallet \
            detail belongs.
    """

    __tablename__ = "wallet_detail"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)  # wallet name
    wallet_tag = Column(String, nullable=False)

    payment_options = relationship(
        "PaymentOption", back_populates="wallet", lazy="joined"
    )


class LinkDetail(Base):  # type: ignore
    """
    Link detail model:

    Attributes:
        id (str): The id of the link detail.
        organization_id (str): The id of the organization to which the \
            link detail belongs.
        name (str): The name of the payment link.
        payment_link (str): The payment link.

    relationship:
        payment_options (object): The payment options to which the link \
            detail belongs.
    """

    __tablename__ = "link_detail"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)  # payment link name
    payment_link = Column(String, nullable=False)

    payment_options = relationship(
        "PaymentOption", back_populates="payment_link", lazy="joined"
    )
