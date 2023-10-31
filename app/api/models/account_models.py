"""This file contains the models for the account table."""
from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class Account(Base):  # type: ignore # pylint: disable=too-few-public-methods
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
        password: This is the password of the user.
        is_active: This is the status of the user.

    """

    __tablename__ = "account"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Integer, default=0)
