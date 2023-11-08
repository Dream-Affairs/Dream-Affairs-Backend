from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.models.account_models import Account
from app.api.schemas.account_schemas import AccountResponse, AccountSchema
from app.database.connection import get_db
from app.services.account_services import (
    create_access_token,
    hash_password,
    verify_password,
)

BASE_URL = "/auth"

router = APIRouter(
    prefix=BASE_URL,
    tags=["Auth"]
)


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


@router.post("/login")
def login(
    user_crdentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(Account).filter(
        Account.email == user_crdentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    if not verify_password(user_crdentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    # create access token
    access_token = create_access_token(data={"account_id": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
