"""This module defines Pydantic schemas for registy/gift."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class GiftType(str, Enum):
    """Represents the enum for accepted gift type."""

    PHYSICAL = "physical"
    CASH = "cash"


class GiftAmountType(str, Enum):
    """Represents the enum for accepted gift amount type."""

    FIXED = "fixed"
    ANY = "any"


class FilterParamEnum(str, Enum):
    """Represents the enum for filter_parameter."""

    ALL = "all"
    AVAILABLE = "available"
    RESERVED = "reserved"
    PURCHASED = "purchased"


class PaymentType(str, Enum):
    """Represents the enum for payment type."""

    BANK = "bank"
    WALLET = "wallet"
    LINK = "link"


class FilterAcountsEnum(str, Enum):
    """Represents the enum for filtering payment accounts."""

    ALL = "all"
    DEFAULT = "default"


class GiftSchema(BaseModel):  # type: ignore
    """Represents the base schema for a gift."""

    title: str
    product_unit_price: Optional[float] = None
    product_quantity: Optional[int] = None
    currency: str
    gift_type: GiftType
    product_image_url: str
    description: Optional[str] = None


class AddProductGift(GiftSchema):
    """Represents the schema for adding product gift."""

    product_url: str

    class Config:
        """Repersents the config model for this Schema
        form_attributes:
            Converts sqlalchemy models to dictionarits for smooth parsing"""

        from_attributes = True


class EditProductGift(AddProductGift):
    """Represents the schema for adding product gift."""

    is_gift_hidden: bool

    class Config:
        """Repersents the config model for this Schema."""

        from_attributes = True


class FilterGiftSchema(BaseModel):  # type: ignore
    """Represents the schema for filtering gifts."""

    filter_parameter: FilterParamEnum = FilterParamEnum.ALL
    filter_by_date: bool | None = False
    start_date: datetime | None = None
    end_date: datetime | None = None


class BankSchema(BaseModel):  # type: ignore
    """Represents the schema for bank account details."""

    name: str
    account_name: str
    account_number: str
    is_default: bool | None = False


class WalletSchema(BaseModel):  # type: ignore
    """Represents the schema for wallet details."""

    name: str
    wallet_tag: str
    is_default: bool | None = False


class LinkSchema(BaseModel):  # type: ignore
    """Represents the schema for payment link details."""

    name: str
    payment_link: str
    is_default: bool | None = False


class PaymentOption(BaseModel):  # type: ignore
    """Represent the schema for a gift payment option."""

    payment_type: PaymentType
    payment_option_id: str


class AddCashGift(GiftSchema):
    """Represents the schema for cash funds gift."""

    gift_amount_type: GiftAmountType
    is_gift_amount_hidden: Optional[bool] = None
    product_total_amount: Optional[float] = None
    payment_options: List[PaymentOption]

    class Config:
        """Repersents the config model for this Schema."""

        from_attributes = True


class EditCashGift(AddCashGift):
    """Represents the schema for updating cash funds gift."""

    is_gift_hidden: bool

    class Config:
        """Repersents the config model for this Schema."""

        from_attributes = True
