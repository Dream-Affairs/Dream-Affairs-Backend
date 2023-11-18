"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.gift_services import add_cash_gift

gift_router = APIRouter(prefix="/registry", tags=["Registry"])


@gift_router.post("/add-cash-gift")
async def add_cash_funds(
    member_id: str,
    gift_image: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
) -> Any:
    """Add a New product gift to Registry.

    Request:
        Method: POST
        member_id: account_id for authentication
            "c4b0baa24a3c47fc9d34681472694f9d"
        gift_item : Request Body containing the details of the
            cash funds gift to be added.
        db(Session): the database session

    Response: Returns CustomResponse with 201 status code and
        data.

    Raises:
        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """

    # gift_item = {
    #     "title": title,
    #     "description": description,
    #     "product_unit_price": product_unit_price,
    #     "product_quantity": product_quantity,
    #     "currency": currency,
    #     "gift_type": gift_type,
    #     "gift_amount_type": gift_amount_type,
    #     "product_total_amount": product_total_amount,
    #     "is_gift_amount_hidden": is_gift_amount_hidden,
    #     "payment_link": payment_link,
    # }
    response, exception = add_cash_gift(
        payment_data={},
        gift_image=gift_image,
        member_id=member_id,
        db=db,
    )
    if exception:
        raise exception

    return response
