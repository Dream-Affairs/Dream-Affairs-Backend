"""This module defines the FastAPI API endpoints for user authentication."""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.account_schemas import AccountSchema
from app.database.connection import get_db
from app.services.account_services import account_service

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
