"""This module provides functions for handling registry/gift related
operations."""

from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.gift_models import Gift
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import AddProductGift
from app.services.account_services import fake_authenticate


def add_product_gift(
    gift: AddProductGift,
    member_id: str,
    db: Session,
) -> tuple[Any, Any]:
    """Add product gift to the associated authenticated user/organization.

    Args:
        product_data (Dict): The gift data to be added.
        gift_image:
        db (Session): The database session.

    Returns:
        List: [None,Exception] or [Respoonse,None]. return an exception
        or a CustomResponse
    """
    member_org_id = fake_authenticate(member_id, db)

    if not member_org_id:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Invalid member_id"
        )
        return None, exception

    org_id = member_org_id

    product_data = gift.model_dump()
    product_data["organization_id"] = org_id

    new_gift = Gift(**product_data)

    try:
        db.add(new_gift)
        db.commit()
        db.refresh(new_gift)

        response = CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Gift successfully added",
            data=jsonable_encoder(new_gift),
        )
        return response, None

    except InternalError:
        db.rollback()
        exception = CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to add gift",
        )

        return None, exception
