from uuid import uuid4
from sqlalchemy.orm import Session
from app.api.models.account_models import Account
from app.api.schemas.account_schemas import AccountSchema, AccountResponse
from app.services.account_services import hash_password

from fastapi import APIRouter, Depends, HTTPException, status
from app.database.connection import get_db

BASE_URL = "/auth"

router = APIRouter(prefix=BASE_URL)


@router.post("/signup/")
def signup(
    user: AccountSchema,
    db: Session = Depends(get_db),
    status_code=status.HTTP_201_CREATED,
    response_model=AccountResponse
) -> AccountResponse:
    """
    Create a new user account.

    Args:
        user (AccountSchema): The user account information.
        db (Session): The database session. (Dependency)
        status_code (int): The HTTP status code to return. (Default: 201)
        response_model (AccountResponse): The response model for the created account.

    Returns:
        AccountResponse: The created user account.

    Raises:
        HTTPException: If the passwords do not match.
    """

    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user_data = user.model_dump()
    user_data["password_hash"] = hash_password(user_data["password"])
    del user_data["password"]
    del user_data["confirm_password"]
    user_data["id"] = str(uuid4())
    
    new_user = Account(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

