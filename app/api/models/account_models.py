"""This file contains the models for the account table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database.connection import Base

PROVIDER = ENUM("google", "local", name="provider")


class Account(Base):  # type: ignore
    """
    Account:
        This class is used to create the account table.

    Args:
        Base: This is the base class from which all the models inherit.

    attributes:
        id: This is the primary key of the table.
        first_name: This is the first name of the user.
        last_name: This is the last name of the user.
        email: This is the email of the user.
        password_hash: This is the password hash of the user.
        phone_number: This is the phone number of the user.
        is_verified: This is the boolean value which tells whether \
            the user is verified or not.
        is_2fa_enabled: This is the boolean value which tells whether \
            the user has enabled 2fa or not.
        is_deleted: This is the boolean value which tells whether the \
            user is deleted or not.
        created_at: This is the date and time when the user was created.
        updated_at: This is the date and time when the user was updated.
        deleted_at: This is the date and time when the user was deleted.

    Relationships:
        auth: This is the relationship between the account and auth table.
        organizations: This is the relationship between the account \
            and organization table.
    """

    __tablename__ = "account"
    id = id = Column(String, primary_key=True, default=uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    phone_number = Column(String(16))
    is_verfiied = Column(Boolean, default=False)
    is_2fa_enabled = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    auth = relationship("Auth", backref="account", lazy=True)
    organizations = relationship("Organization", backref="account", lazy=True)


class Auth(Base):  # type: ignore
    """
    Auth:

    This class is used to create the auth table.

    Args:
        Base: This is the base class from which all the models inherit.

    attributes:
        id: This is the primary key of the table.
        account_id: This is the foreign key of the account table.
        provider: This is the provider of the user.
        setup_date: This is the date when the user setup \
            the provider for the first time.
    """

    __tablename__ = "auth"
    id = Column(String, primary_key=True, default=uuid4)
    account_id = Column(String, ForeignKey("account.id"), nullable=False)
    provider = Column(PROVIDER, nullable=False)

    setup_date = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", backref="auth", lazy=True)
