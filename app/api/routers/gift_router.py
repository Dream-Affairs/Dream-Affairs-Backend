"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomException
from app.api.schemas.gift_schemas import AddProductGift
from app.database.connection import get_db
from app.services.gift_services import (
    add_product_gift,
    create_blob,
    fake_authenticate,
)

gift_router = APIRouter(prefix="/registry", tags=["Registry"])


@gift_router.post("/upload-gift-image")
async def upload_gift_image(
    member_id: str,
    gift_image: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
) -> Any:
    """Upload a gift image to cloud.

    Args:
        member_id: the id to authenticate the user\
        (9174b84cf01f49a4ab26a79e736fbdff).
        gift_image: the file to use as gift image
        db: database session.

    Return: returns CustomResponse containing the product_image_url

    Exception:
        raises a CustomException if failed to create blob
    """
    # fake authenticate the user
    member_org_id = fake_authenticate(member_id, db)

    if not member_org_id:
        err = CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Invalid member_id"
        )
        raise err

    response = create_blob(member_org_id, gift_image)

    return response


@gift_router.post("/add-product-gift")
async def add_product(
    member_id: str,
    gift_item: AddProductGift,
    db: Session = Depends(get_db),
) -> Any:
    """Add a New product gift to Registry.

    Request:
        Method: POST
        member_id: account_id for authentication
            "9174b84cf01f49a4ab26a79e736fbdff"
        gift_item(AddProductGift): Request Body containing the details of the
            product gift to be added.
        db(Session): the database session

    Response: Returns CustomResponse with 201 status code and
        data.

    Exception:
        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """

    response, exception = add_product_gift(
        gift=gift_item,
        member_id=member_id,
        db=db,
    )
    if exception:
        raise exception

    return response
