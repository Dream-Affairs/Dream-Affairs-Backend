from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.models.account_models import Account, Auth
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.account_schemas import AccountSchema
from app.database.connection import get_db
from app.services.account_services import hash_password

BASE_URL = "/auth"

router = APIRouter(prefix=BASE_URL, tags=['Auth'])


@router.post("/signup/")
def signup(
    user: AccountSchema,
    db: Session = Depends(get_db),
):
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

    new_auth = Auth(
        id=str(uuid4()),
        account_id=new_user.id,
        provider="local",
        setup_date=new_user.created_at
    )

    db.add(new_auth)
    db.commit()
    db.refresh(new_auth)

    return CustomResponse(
        status_code=status.HTTP_201_CREATED,
        message="Account created successfully",
        data=user_data,
    )
