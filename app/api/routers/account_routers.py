"""This module defines the FastAPI API endpoints for user authentication."""


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.models.account_models import Account
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.account_schemas import AccountSchema
from app.database.connection import get_db
from app.services.account_services import (
    account_service,
    create_access_token,
    verify_password,
)

BASE_URL = "/auth"

router = APIRouter(prefix=BASE_URL, tags=["Auth"])


@router.post("/signup")
def signup(
    user: AccountSchema,
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

    if account_service(user, db):
        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Account created successfully",
            data="",
        )
    raise CustomException(status_code=500, message="Failed to create account")


@router.post("/login")
def login(
    user_crdentials: OAuth2PasswordRequestForm = Depends(),
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

    user = (
        db.query(Account)
        .filter(Account.email == user_crdentials.username)
        .first()
    )

    if not user:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Invalid credentials",
        )

    if not verify_password(user_crdentials.password, user.password_hash):
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Invalid credentials",
        )

    # create access token
    access_token = create_access_token(data={"account_id": user.id})

    return CustomResponse(
        status_code=status.HTTP_200_OK,
        data={"access_token": access_token, "token_type": "bearer"},
    )
