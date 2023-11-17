"""This module defines the FastAPI API endpoints for user authentication."""


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.account_schemas import (
    AccountSchema,
    ForgotPasswordData,
    ResetPasswordData,
)
from app.database.connection import get_db
from app.services.account_services import (
    account_service,
    forgot_password_service,
    login_service,
    reset_password_service,
)
from app.services.email_services import send_company_email_api

BASE_URL = "/auth"

router = APIRouter(prefix=BASE_URL, tags=["Auth"])


@router.post("/signup")
def signup(
    user: AccountSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Create a new user account.

    Args:
        user (AccountSchema): The user account information.
        db (Session): The database session. (Dependency)
        status_code (int): The HTTP status code to return. (Default: 201)
        response_model (AccountResponse): The response model for the created
            account.

    Returns:
        AccountResponse: The created user account.

    Raises:
        HTTPException: If the passwords do not match.
    """

    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    _, err = account_service(user, db)

    if err:
        raise err

    background_tasks.add_task(
        send_company_email_api,
        subject="Welcome to Dream Affairs",
        recipient_email=user.email,
        template="_email_verification.html",
        kwargs={"name": user.first_name, "verification_link": ...},
    )

    return CustomResponse(
        status_code=status.HTTP_201_CREATED,
        message="Account created successfully",
        data="",
    )


@router.post("/login")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Log in a user and generate an access token.

    Args:
        user_credentials: The user's login credentials.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If the provided credentials are invalid.
    """
    return login_service(db, user_credentials)


@router.post("/forgot-password")
def user_forgot_password(
    user_data: ForgotPasswordData,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Handles the request to initiate the password reset process for a user.

    Args:
        request: The incoming request object.
        user_email: The email address of the user.
        db: The database session.

    Returns:
        The result of the forgot password service.
    """

    return forgot_password_service(user_data, db)


@router.post("/reset-password")
def reset_password(
    token_data: ResetPasswordData, db: Session = Depends(get_db)
) -> CustomResponse:
    """Reset the password for an account.

    Args:
        token_data: The data associated with the reset password token.
        db: The database session.

    Returns:
        The result of the `reset_password_service` function.
    """

    return reset_password_service(token_data, db)
