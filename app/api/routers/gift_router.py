"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.gift_services import add_product_gift

gift_router = APIRouter(prefix="/registry", tags=["Registry"])


@gift_router.post("/add-product-gift")
async def add_product(
    member_id: Annotated[str, Form()],
    gift_image: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    product_unit_price: Annotated[float | int, Form()],
    product_quantity: Annotated[int, Form()],
    product_url: Annotated[str, Form()],
    currency: Annotated[str, Form()],
    gift_type: Annotated[str, Form()],
    description: Annotated[str | None, Form()] = None,
    db: Session = Depends(get_db),
) -> Any:
    """Add a New product gift to Registry.

    Request:
        Method: POST
        member_id: account_id for authentication
            "c4b0baa24a3c47fc9d34681472694f9d"
        gift_item : Request Body containing the details of the
            product gift to be added.
        db(Session): the database session

    Response: Returns CustomResponse with 201 status code and
        data.

    Raises:
        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """

    gift_item = {
        "title": title,
        "description": description,
        "product_unit_price": product_unit_price,
        "product_quantity": product_quantity,
        "product_url": product_url,
        "currency": currency,
        "gift_type": gift_type,
    }
    response, exception = add_product_gift(
        product_data=gift_item,
        gift_image=gift_image,
        member_id=member_id,
        db=db,
    )
    if exception:
        raise exception

    return response
