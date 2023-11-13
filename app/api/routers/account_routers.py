"""This module defines the FastAPI API endpoints for user authentication."""


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.account_schemas import AccountSchema
from app.database.connection import get_db
from app.services.account_services import account_service, login_service
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

    if not account_service(user, db):
        raise CustomException(
            status_code=500, message="Failed to create account"
        )
    background_tasks.add_task(
        send_company_email_api,
        subject="Welcome to Dream Affairs",
        recipient=user.email,
        kwargs={...},
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
