"""This module defines Pydantic schemas for payment."""

from enum import Enum

from pydantic import BaseModel


class PaymentType(str, Enum):
    """Represents the enum for payment type."""

    BANK = "bank"
    WALLET = "wallet"
    LINK = "link"


class FilterAcountsEnum(str, Enum):
    """Represents the enum for filtering payment accounts."""

    ALL = "all"
    DEFAULT = "default"


class BankSchema(BaseModel):  # type: ignore
    """Represents the schema for bank account details."""

    name: str
    account_name: str
    account_number: str
    is_default: bool | None = False
    organization_id: str


class WalletSchema(BaseModel):  # type: ignore
    """Represents the schema for wallet details."""

    name: str
    wallet_tag: str
    is_default: bool | None = False
    organization_id: str


class LinkSchema(BaseModel):  # type: ignore
    """Represents the schema for payment link details."""

    name: str
    payment_link: str
    is_default: bool | None = False
    organization_id: str


class PaymentOption(BaseModel):  # type: ignore
    """Represent the schema for a gift payment option."""

    payment_type: PaymentType
    payment_option_id: str
