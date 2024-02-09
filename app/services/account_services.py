"""This module provides functions for handling user account related
operations."""

import base64
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple, Union
from uuid import uuid4

from fastapi import BackgroundTasks, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.middlewares.jwt_bearer import HTTPAuthorizationCredentials
from app.api.models.account_models import Account, Auth
from app.api.responses.custom_responses import CustomException
from app.api.schemas.account_schemas import (
    AccountLogin,
    AccountLoginResponse,
    AccountSignup,
    ForgotPasswordData,
    ResetPasswordData,
    TokenData,
)
from app.core.config import settings
from app.services.email_services import send_email_api

SECRET_KEY = settings.AUTH_SECRET_KEY
ALGORITHM = settings.HASH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(
    user: Account,
) -> Tuple[AccountLoginResponse, CustomException]:
    """
    Authenticate user:

    This function authenticates a user and generates an access token
    that allows the user to access protected endpoints.

    The function takes a user object and a database session as arguments.
    It generates an access token for the user and returns the token and
    user verification status.

    Args:

    - user: The user object.
    - db: The database session.

    Returns:

    - Tuple[AccountLoginResponse, CustomException]: A tuple containing the
        user verification status and the access token, or a\
              CustomException
        if the user credentials are invalid.

    Example:

    ```python
    from app.api.models.account_models import Account
    from app.api.schemas.account_schemas import AccountLoginResponse
    from app.api.responses.custom_responses import CustomException
    from app.services.account_services import authenticate_user

    user = Account(
        id="123",
        email="example@email.com",
        first_name="John",
        password_hash="hashed_password",
        is_verified=True,
        is_2fa_enabled=False,
    )
    res, err = authenticate_user(user)
    if err:
        raise err

    print(res)
    ```
    """
    if user:
        access_token = generate_token(
            data={
                "account_id": user.id,
            },
            expire_mins=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return (
            AccountLoginResponse(
                is_verified=user.is_verified,
                token=access_token,
                is_2fa_enabled=user.is_2fa_enabled,
            ).model_dump(),
            None,
        )
    return None, CustomException(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Invalid credentials",
    )


def create_account(
    user: AccountSignup, background_tasks: BackgroundTasks, db: Session
) -> Tuple[bool, CustomException]:
    """
    Create account:

    This function creates a new user account and sends a verification email
    to the user.

    The function takes a user object, a background task, and a database
    session as arguments. It creates a new user account, generates a
    verification token, and sends a verification email to the user.

    Args:

    - user: The user object.
    - background_tasks: The background task.
    - db: The database session.

    Returns:

    - Tuple[bool, CustomException]: A tuple containing a boolean indicating
        the success of the account creation and a CustomException if the
        account creation fails.

    Example:

    ```python
    from app.api.models.account_models import Account
    from app.api.schemas.account_schemas import AccountSignup
    from app.api.responses.custom_responses import CustomException
    from app.services.account_services import create_account

    user = AccountSignup(
        email="example@email.com",
        first_name="John",
        password="password",
        provider="email",
    )

    res, err = create_account(user)
    if err:
        raise err

    print(res)
    """

    existing_user = (
        db.query(Account).filter(Account.email == user.email).first()
    )

    if existing_user:
        return None, CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="User already exists",
        )

    new_user_id = (uuid4().hex,)
    new_user = Account(
        id=new_user_id,
        email=user.email,
        first_name=user.first_name,
        password_hash=hash_password(user.password),
        auth=Auth(
            id=uuid4().hex,
            account_id=new_user_id,
            provider=user.provider,
        ),
    )

    if not add_to_db(db, new_user):
        return None, CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="failed to create account",
        )

    access_token = generate_token(
        data={"account_id": new_user.id, "context": "verify-account"},
        expire_mins=10,
    )
    url = f"{settings.FRONT_END_HOST}/auth/verify-account?token={access_token}"

    background_tasks.add_task(
        send_email_api,
        subject="Welcome to Dream Affairs",
        recipient_email=user.email,
        template="_email_verification.html",
        # db=db,
        kwargs={"name": user.first_name, "verification_link": url},
    )

    return True, None


def login_service(
    db: Session, user_credentials: AccountLogin
) -> Tuple[AccountLoginResponse, CustomException]:
    """
    Login service:

    This function authenticates a user and generates an access token
    that allows the user to access protected endpoints.

    The function takes a user object and a database session as arguments.
    It generates an access token for the user and returns the token and
    user verification status.

    Args:

    - user: The user object.
    - db: The database session.

    Returns:

    - Tuple[AccountLoginResponse, CustomException]: A tuple containing the
        user verification status and the access token, or a\
                CustomException
        if the user credentials are invalid.

    Example:

    ```python
    from app.api.models.account_models import Account
    from app.api.schemas.account_schemas import AccountLoginResponse
    from app.api.responses.custom_responses import CustomException
    from app.services.account_services import authenticate_user

    user = AccountLogin(
        email="example@email.com",
        password="password",
        provider="email",
    )
    res, err = login_service(db, user)
    if err:
        raise err

    print(res)
    ```
    """

    user = get_account_by_email(db, user_credentials.email)

    if user is not None:
        if user_credentials.provider == "google" or verify_password(
            user_credentials.password, user.password_hash
        ):
            return authenticate_user(user)

    return None, CustomException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message="Invalid credentials",
    )


def verify_account_service(
    token_data: str, db: Session
) -> Tuple[str, CustomException]:
    """
    Verify account service:

    This function verifies a user account using a verification token.

    The function takes a verification token and a database session as
    arguments. It verifies the user account and returns a message indicating
    the success of the verification.

    Args:

    - token_data: The data associated with the verification token.
    - db: The database session.

    Returns:

    - Tuple[str, CustomException]: A tuple containing a message indicating

    Example:

    ```python
    from app.api.models.account_models import Account
    from app.api.schemas.account_schemas import VerifyAccountTokenData
    from app.api.responses.custom_responses import CustomException
    from app.services.account_services import verify_account_service

    token = VerifyAccountTokenData(
        token
    )
    res, err = verify_account_service(token, db)
    if err:
        raise err

    print(res)
    ```
    """

    account_id, context = decode_token(token_data)

    if context != "verify-account":
        return None, CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid token",
        )

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None, CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Account not found"
        )
    if account.is_verified:
        return None, CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Account already verified",
        )
    account.is_verified = True
    db.commit()

    return "Success", None


def forgot_password_service(
    user_data: ForgotPasswordData,
    background_tasks: BackgroundTasks,
    db: Session,
) -> Tuple[str, CustomException]:
    """
    Forgot password service:

    This function initiates the password reset process for a user.

    The function takes a user email and a database session as arguments.
    It generates a reset password token and sends a reset password email to
    the user.

    Args:

    - user_data: The user email.
    - db: The database session.

    Returns:

    - Tuple[str, CustomException]: A message indicating the success of the
        password reset, or a CustomException if the account is not found.

    Example:

    ```python
    from app.api.schemas.account_schemas import ForgotPasswordData
    from app.api.responses.custom_responses import CustomException
    from app.services.account_services import forgot_password_service

    user = ForgotPasswordData(
        email="example@email.com",
    )
    res, err = forgot_password_service(user, db)
    if err:
        raise err

    print(res)
    ```
    """

    account = (
        db.query(Account).filter(Account.email == user_data.email).first()
    )
    if account:
        access_token = generate_token(
            data={"account_id": account.id, "context": "reset-password"},
            expire_mins=10,
        )
        url = f"{settings.FRONT_END_HOST}/auth/reset-password\
?token={access_token}"

        # fix later send reset password email
        background_tasks.add_task(
            send_email_api,
            subject="Password Reset",
            recipient_email=user_data.email,
            template="_email_forgot_password.html",
            # db=db,
            kwargs={"name": account.first_name, "reset_link": url},
        )
        msg = f"""
An email has been sent to {user_data.email} with a link for password reset."""
        return msg, None

    return None, CustomException(
        status_code=status.HTTP_404_NOT_FOUND,
        message="No account found with that email",
    )


def reset_password_service(
    token_data: ResetPasswordData,
    db: Session,
    background_tasks: BackgroundTasks,
) -> Tuple[str, CustomException]:
    """
    Reset password service:

    This function resets the password for a user account.

    The function takes a reset password token and a database session as
    arguments. It resets the user account password and returns a message

    Args:

    - token_data: The data associated with the reset password token.
    - db: The database session.

    Returns:

    - Tuple[str, CustomException]: A message indicating the success of the
        password reset, or a CustomException if the token is invalid.

    Example:

    ```python
    from app.api.schemas.account_schemas import ResetPasswordData
    from app.api.responses.custom_responses import CustomException
    from app.services.account_services import reset_password_service

    token = ResetPasswordData(
        token,
        password,
        confirm_password
    )
    res, err = reset_password_service(token, db)
    if err:
        raise err

    print(res)
    ```
    """
    if token_data.password != token_data.confirm_password:
        return None, CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Passwords do not match",
        )

    account_id, context = decode_token(token_data.token)

    if context != "reset-password":
        return None, CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid or expired link",
        )

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None, CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Account not found"
        )

    # Set the new password
    hashed_password = hash_password(token_data.password)
    account.password_hash = hashed_password
    db.commit()

    background_tasks.add_task(
        send_email_api,
        subject="Password Reset",
        recipient_email=account.email,
        template="_email_reset_password.html",
        # db=db,
        kwargs={"name": account.first_name},
    )
    return "success", None


def hash_password(password: str) -> Any:
    """Hashes a password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        str: The result of the password verification.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(
    data: Dict[str, Any],
    expire_mins: int,
) -> str:
    """Create an access token.

    Args:
        data (dict): The data to encode into the access token.

    Returns:
        str: The generated access token.
    """

    expire = datetime.utcnow() + timedelta(minutes=expire_mins)
    data["exp"] = expire
    data["iat"] = datetime.utcnow()
    data["iss"] = "dream-affairs"
    data["aud"] = "dream-affairs"

    return encode_data(jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM))


def decode_token(
    token: HTTPAuthorizationCredentials, is_authenticate: bool = False
) -> Dict[str, Any] | Tuple[str, str]:
    """Decode a token.

    Args:
    """
    token = extract_token(token)
    try:
        data = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer="dream-affairs",
            audience="dream-affairs",
            options={"verify_exp": True},
        )
    except ExpiredSignatureError as e:
        print(e)
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="token expired",
        ) from e

    except JWTError as e:
        print(e)
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
        ) from e

    if is_authenticate:
        return data
    return data.get("account_id"), data.get("context")


def verify_access_token(token: str) -> TokenData:
    """Verify an access token.

    Args:
        token (str): The access token to verify.
        credentials_exception: The exception to raise if the token is invalid.

    Returns:
        TokenData: The token data extracted from the access token.

    Raises:
        credentials_exception: If the access token is invalid.
    """
    account_id, _ = decode_token(token)
    return TokenData(id=account_id)


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


def get_account_by_email(db: Session, email: str) -> Account:
    """Get account by email.

    Args:
        db: The database session.
        email: The email address of the account.

    Returns:
        Account: The account object.
    """
    user = db.query(Account).filter(Account.email == email).first()

    if user is not None:
        return user
    return None


def encode_data(data: Any) -> str:
    """Encode a dictionary of data into a base64 string.

    Args:
        data (dict): The data to encode.

    Returns:
        str: The encoded data.
    """
    return base64.b64encode(str(data).encode("ascii")).decode("ascii")


def decode_data(data: Any) -> bytes:
    """Decode a base64 string into a dictionary of data.

    Args:
        data (str): The data to decode.

    Returns:
        bytes: The decoded data.
    """
    return base64.b64decode(data).decode("ascii")


def extract_token(token):
    """
    Extract token:

    The function takes a token and extracts the token from the request.

    Args:

    - token: The token.

    Returns:

    - str: The extracted token.
    """
    if isinstance(token, HTTPAuthorizationCredentials):
        token = token.credentials
        token = decode_data(token)
    else:
        token = decode_data(token)
    token = token.split("Bearer ")[0]

    return token
