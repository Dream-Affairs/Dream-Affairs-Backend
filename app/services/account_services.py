"""This module provides functions for handling user account related
operations."""

import base64
from datetime import datetime, timedelta
from typing import Any, Dict, Union
from uuid import uuid4

from fastapi import BackgroundTasks, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.middlewares.jwt_bearer import HTTPAuthorizationCredentials
from app.api.models.account_models import Account, Auth
from app.api.models.organization_models import (
    Organization,
    OrganizationDetail,
    OrganizationMember,
)
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.account_schemas import (
    AccountLogin,
    AccountSignup,
    ForgotPasswordData,
    ResetPasswordData,
    TokenData,
    VerifyAccountTokenData,
)
from app.core.config import settings
from app.services.email_services import send_email_api
from app.services.roles_services import RoleService

SECRET_KEY = settings.AUTH_SECRET_KEY
ALGORITHM = settings.HASH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(user: Account, db: Session):
    """Authenticate user and generate access token.

    Args:
        user: The user object.
        db: The database session.

    Returns:
        CustomResponse: The response containing the access
            token and token type.
    """
    if user:
        user_org = (
            db.query(OrganizationMember)
            .filter(OrganizationMember.account_id == user.id)
            .first()
        )

        access_token = generate_token(
            data={
                "account_id": user.id,
            },
            expire_mins=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return CustomResponse(
            status_code=status.HTTP_200_OK,
            data={
                "user": {
                    "id": user.id,
                },
                "organization": {
                    "organization_id": user_org.organization_id,
                    "organization_member_id": user_org.id,
                },
                "access_token": access_token,
            },
        )

    return CustomResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        message="User not found",
    )


def create_account(
    user: AccountSignup, background_tasks: BackgroundTasks, db: Session
) -> Any:
    """Create a new user account and associated authentication record.

    Args:
        user (AccountSignup): The user account data.
        db (Session): The database session.

    Returns:
        bool: True if the user account and authentication record were
            successfully created, False otherwise.
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

    org_id = (uuid4().hex,)
    org = Organization(
        id=org_id,
        name=f"{new_user.first_name} & {user.partner_name}".title(),
        owner=new_user.id,
        org_type="Wedding",
        detail=OrganizationDetail(
            organization_id=org_id,
            event_location=user.location,
            website=f"/{user.first_name}-{user.partner_name}".lower(),
            event_date=user.event_date,
        ),
    )

    if not add_to_db(db, new_user, org):
        return None, CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="failed to create account",
        )

    role = RoleService().get_default_role(db=db, name="Admin")
    org_role = RoleService().add_role_to_organization(
        db, org.id, role_id=role.id
    )

    RoleService().assign_role(
        organization_id=org.id,
        db=db,
        organization_role_id=org_role.id,
        account_id=new_user.id,
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
        organization_id=org.id,
        db=db,
        kwargs={"name": user.first_name, "verification_link": url},
    )

    return True, None


def verify_account_service(
    token_data: VerifyAccountTokenData, db: Session
) -> CustomResponse:
    """Verify an account using a verify account token.

    Args:
        token_data (VerifyAccountTokenData): The data associated with
            the verify account token.
        db (Session): The database session.

    Returns:
        CustomResponse: The response containing a "message" key indicating the
            success of the verified account.

    Raises:
        CustomException: If wrong token context, the token is invalid
        or expired, or the account is not found.
    """

    account_id, context = decode_token(token_data.token)

    if context != "verify-account":
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid token",
        )

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Account not found"
        )

    account.is_verified = True
    add_to_db(db, account)

    return CustomResponse(
        status_code=status.HTTP_200_OK, message="Verification successful"
    )


def login_service(
    db: Session, user_credentials: AccountLogin
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

    user = get_account_by_email(db, user_credentials.email)

    if user_credentials.provider == "google":
        return authenticate_user(user, db)

    if user and verify_password(user_credentials.password, user.password_hash):
        return authenticate_user(user, db)

    raise CustomException(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Invalid credentials",
    )


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
        access_token = generate_token(
            data={"account_id": account.id, "context": "reset-password"},
            expire_mins=10,
        )
        url = f"{settings.FRONT_END_HOST}/auth/reset-password\
?token={access_token}"
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
        status_code=status.HTTP_404_NOT_FOUND,
        message="No account found with that email",
    )


def reset_password_service(
    token_data: ResetPasswordData, db: Session
) -> CustomResponse:
    """Reset the password for an account using a reset password token.

    Args:
        token_data (ResetPasswordData): The data associated with
            the reset password token.
        db (Session): The database session.

    Returns:
        dict: A dictionary with a "message" key indicating the
            success of the password reset.

    Raises:
        CustomException: If the passwords do not match, the token is invalid
        or expired, or the account is not found.
    """
    if token_data.password != token_data.confirm_password:
        raise CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Passwords do not match",
        )

    account_id, context = decode_token(token_data.token)

    if context != "reset-password":
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid or expired link",
        )

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Account not found"
        )

    # Set the new password
    hashed_password = hash_password(token_data.password)
    account.password_hash = hashed_password
    add_to_db(db, account)

    return CustomResponse(
        status_code=status.HTTP_200_OK, message="Password reset successful"
    )


# remove this function when auth is implemented
def fake_authenticate(member_id: str, db: Session) -> Any:
    """This functions tries to mimic auth for a user
    Arg:
    member_id: the ID to validate and authenticate
    db: the database session.
    Return: if Authenticated return the org_id which the user belong to,
        if fails, return False.
    """
    authenticate_member = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.id == member_id)
        .first()
    )
    if not authenticate_member:
        return False

    org_id = authenticate_member.organization_id
    return org_id


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
) -> Any:
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
) -> Dict[str, Any] | tuple:
    """Decode a JWT token and retrieve the account ID.

    Args:
        token: The JWT token to decode.
        credentials_exception: The exception to raise if the account
            ID is not found.

    Returns:
        str: The decoded account ID.

    Raises:
        credentials_exception: If the account ID is not found in the decoded
            token.
        JWTError: If an error occurs during JWT decoding.
    """

    token = decode_data(token).split("Bearer ")[0]
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
    return db.query(Account).filter(Account.email == email).first()


def encode_data(data: Any) -> str:
    """Encode a dictionary of data into a base64 string.

    Args:
        data (dict): The data to encode.

    Returns:
        str: The encoded data.
    """
    return base64.b64encode(str(data).encode("ascii")).decode("ascii")


def decode_data(data: Any) -> Any:
    """Decode a base64 string into a dictionary of data.

    Args:
        data (str): The data to decode.

    Returns:
        Any: The decoded data.
    """
    return base64.b64decode(data).decode("ascii")
