"""This module provides functions for handling user account related
operations."""

from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.models.account_models import Account, Auth
from app.api.schemas.account_schemas import AccountSchema, TokenData
from app.core.config import settings

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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: Column[str]) -> Any:
    """Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        str: The result of the password verification.
    """

    return pwd_context.verify(plain_password, hashed_password)


SECRET_KEY = settings.AUTH_SECRET_KEY
ALGORITHM = settings.HASH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: Dict[str, Any]) -> Any:
    """Create an access token.

    Args:
        data (dict): The data to encode into the access token.

    Returns:
        str: The generated access token.
    """

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(
    token: str, credentials_exception: HTTPException
) -> TokenData:
    """Verify an access token.

    Args:
        token (str): The access token to verify.
        credentials_exception: The exception to raise if the token is invalid.

    Returns:
        TokenData: The token data extracted from the access token.

    Raises:
        credentials_exception: If the access token is invalid.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account_id: str = payload.get("account_id")

        if account_id is None:
            raise credentials_exception
        token_data = TokenData(id=account_id)
    except JWTError as exc:
        raise credentials_exception from exc

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Get the current user based on the provided access token.

    Args:
        token (str, optional): The access token.

    Returns:
        TokenData: The token data representing the current user.

    Raises:
        HTTPException: If the credentials cannot be validated.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(token, credentials_exception)
