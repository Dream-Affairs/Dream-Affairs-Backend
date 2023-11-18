"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.gift_schemas import AddProductGift
from app.database.connection import get_db
from app.services.gift_services import add_product_gift

gift_router = APIRouter(prefix="/registry", tags=["Registry"])


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
