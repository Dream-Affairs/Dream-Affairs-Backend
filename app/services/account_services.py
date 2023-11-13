"""This module provides functions for handling user account related
operations."""

from datetime import datetime, timedelta
from typing import Any, Dict, Union
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.models.account_models import Account, Auth
from app.api.models.organization_models import Organization, OrganizationDetail
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.account_schemas import (
    AccountSchema,
    ForgotPasswordData,
    TokenData,
)
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

    new_user = Account(
        id=uuid4().hex,
        email=user.email,
        first_name=user.first_name,
        password_hash=hash_password(user.password),
    )

    auth = Auth(
        id=uuid4().hex,
        account_id=new_user.id,
        provider="local",
        setup_date=new_user.created_at,
    )

    org = Organization(
        id=uuid4().hex,
        name=f"{new_user.first_name} & {user.partner_name}".title(),
        owner=new_user.id,
        org_type="Wedding",
    )

    org_detail = OrganizationDetail(
        organization_id=org.id,
        event_location=user.location,
        website=f"/{user.first_name}-{user.partner_name}".lower(),
        event_date=user.event_date,
    )

    return add_to_db(db, new_user, auth, org, org_detail)


def add_to_db(db: Session, *args: Union[Any, Any]) -> bool:
    """Adds the given objects to the database.

    Args:
        db: The database session.
        *args: The objects to be added to the database.

    Returns:
        bool: True if all objects were successfully added, False otherwise.
    """

    for arg in args:
        try:
            db.add(arg)
            db.commit()
            db.refresh(arg)
        except IntegrityError as e:
            print(e)
            db.rollback()
            return False
    return True


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


def login_service(
    db: Session, user_credentials: OAuth2PasswordRequestForm = Depends()
) -> CustomResponse:
    """Authenticates a user and generates an access token.

    Args:
        db: The database session.
        user_crdentials: The user credentials.

    Returns:
        CustomResponse: The response containing the access
            token and token type.

    Raises:
        CustomException: If the user credentials are invalid.
    """

    user = (
        db.query(Account)
        .filter(Account.email == user_credentials.username)
        .first()
    )

    if user and verify_password(user_credentials.password, user.password_hash):
        access_token = create_access_token(
            data={"account_id": user.id},
            expire_mins=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return CustomResponse(
            status_code=status.HTTP_200_OK,
            data={"access_token": access_token, "token_type": "bearer"},
        )

    raise CustomException(
        status_code=status.HTTP_403_FORBIDDEN,
        message="Invalid credentials",
    )


def create_access_token(data: Dict[str, Any], expire_mins: int) -> Any:
    """Create an access token.

    Args:
        data (dict): The data to encode into the access token.

    Returns:
        str: The generated access token.
    """

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=expire_mins)
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


def forgot_password_service(
    user_data: ForgotPasswordData, db: Session
) -> CustomResponse:
    """The function retrieves the user account, generates a password reset
    token and URL.

    Args:
        user_data: The data required for the forgot password request.
        db: The database session.

    Returns:
        CustomResponse: The response indicating the status of the \
        forgot password request.

    Raises:
        CustomException: If an unexpected error occurs.
    """

    account = (
        db.query(Account).filter(Account.email == user_data.email).first()
    )
    if account:
        access_token = create_access_token(
            data={"account_id": account.id}, expire_mins=10
        )
        url = f"/api/v1/auth/reset-password?token={access_token}"
        print(url)  # temporary

        try:
            # send reset password email
            # send_reset_password_mail(
            #     recipient_email=user_email,
            #     user=user,
            #     url=url
            # )
            return CustomResponse(
                status_code=200,
                message=f"An email has been sent to {user_data.email} with a \
                link for password reset.",
            )
        except ValueError as e:
            print(e)

    raise CustomException(
        status_code=500, detail="An unexpected error occurred"
    )
