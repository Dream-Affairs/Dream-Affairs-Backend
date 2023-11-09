"""This module provides functions for handling user account related
operations."""

from typing import Any
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.models.account_models import Account, Auth
from app.api.schemas.account_schemas import AccountSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> Any:
    """Hashes a password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def account_service(user: AccountSchema, db: Session) -> bool:
    """Create a new user account and associated authentication record.

    Args:
        user (AccountSchema): The user account data.
        db (Session): The database session.

    Returns:
        bool: True if the user account and authentication record were
            successfully created, False otherwise.
    """

    existing_user = (
        db.query(Account).filter(Account.email == user.email).first()
    )
    if existing_user:
        return False

    user_data = user.model_dump()
    user_data["password_hash"] = hash_password(user_data["password"])
    del user_data["password"]
    del user_data["confirm_password"]
    user_data["id"] = uuid4().hex

    new_user = Account(**user_data)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        print(e)
        db.rollback()
        return False

    new_auth = Auth(
        id=uuid4().hex,
        account_id=new_user.id,
        provider="local",
        setup_date=new_user.created_at,
    )
    try:
        db.add(new_auth)
        db.commit()
        db.refresh(new_auth)

        return True
    except IntegrityError as e:
        print(e)
        db.rollback()
        return False
