"""This module provides functions for handling registry/gift related
operations."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.gift_models import Gift, PaymentOption
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import (
    AddCashGift,
    AddProductGift,
    EditCashGift,
    EditProductGift,
    FilterGiftSchema,
)


def add_product_gift_(
    gift_item: AddProductGift,
    organization_id: str,
    db: Session,
) -> tuple[Any, Any]:
    """Add Physical gift to the associated organization.

    Args:
        gift_item (Dict): The gift data to be added.
        db (Session): The database session.
    Returns:
        List: [None,Exception] or [Respoonse,None]. return an exception
        or a CustomResponse
    """

    gift_item = gift_item.model_dump()
    gift_item["organization_id"] = organization_id

    new_gift = Gift(**gift_item, id=uuid4().hex)

    try:
        db.add(new_gift)
        db.commit()
        db.refresh(new_gift)

        response = CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Gift successfully added",
            data=jsonable_encoder(new_gift, exclude=["organization"]),
        )
        return response, None

    except InternalError:
        db.rollback()
        exception = CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to add gift",
        )

        return None, exception


def edit_product_gift_(
    gift_item: EditProductGift,
    gift_id: str,
    db: Session,
) -> tuple[Any, Any]:
    """Edit product gift  associated with user/organization.

    Args:
        gift_item(Dict): The gift data to be updated.
        db (Session): The database session.
    Returns:
        List: [None,Exception] or [Respoonse,None]. return an exception
        or a CustomResponse
    """
    gift_instance = db.query(Gift).filter(Gift.id == gift_id).first()

    if not gift_instance:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Invalid gift_id"
        )
        return None, exception

    gift_item = gift_item.model_dump(exclude_unset=True)

    try:
        for key, value in gift_item.items():
            setattr(gift_instance, key, value)
        db.commit()
        db.refresh(gift_instance)

        response = CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Gift successfully updated",
            data=jsonable_encoder(gift_instance, exclude=["organization"]),
        )
        return response, None

    except InternalError:
        db.rollback()
        exception = CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update gift",
        )

        return None, exception


def fetch_gift(gift_id: str, db: Session) -> tuple[Any, Any]:
    """Fetch a gift associated with the gift_id.

    Args:
        gift_id(str): The specific gift ID
        db (Session): The database session.
    Returns:
        List: [None,Exception] or [Respoonse,None]. return an exception
        or a CustomResponse containing gift data.
    """
    gift_instance = db.query(Gift).filter(Gift.id == gift_id).first()

    if not gift_instance:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Invalid gift_id"
        )
        return None, exception
    if gift_instance.is_deleted:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="The gift doesn't exist, It must have been deleted",
        )
        return None, exception

    response = CustomResponse(
        status_code=status.HTTP_200_OK,
        message="success",
        data=jsonable_encoder(gift_instance, exclude=["organization"]),
    )
    return response, None


def delete_a_gift(gift_id: str, db: Session) -> tuple[Any, Any]:
    """Delete a gift associated with the gift_id.

    Args:
        gift_id(str): The specific gift ID
        db (Session): The database session.
    Returns:
        List: [None,Exception] or [Respoonse,None]. return an exception
        or a CustomResponse containing gift data.
    """
    gift_instance = db.query(Gift).filter(Gift.id == gift_id).first()

    if not gift_instance:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid gift_id",
        )
        return None, exception

    if gift_instance.is_deleted:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="The gift doesn't exist, It must have been deleted",
        )
        return None, exception

    gift_instance.is_deleted = True
    gift_instance.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(gift_instance)

    response = CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Gift deleted successfully",
    )
    return response, None


def gifts_filter(
    org_id: str,
    params: FilterGiftSchema,
    db: Session,
) -> tuple[Any, Any]:
    """Fetch all gifts that are not deleted and not hidden under a specified
    parameter based org_id provided.

    Args:
        org_id : str,
        params(FilterGiftSchema):
            filter_parameter: str,
            filter_by_date:bool,
            start_date: datetime,
            end_date: datetime
        db (Session): The database session.
    Returns:
        Tuple: [None,Exception] or [Response,None]
    """
    # instance of a base query
    base_query = db.query(Gift).filter_by(
        is_deleted=False,
        is_gift_hidden=False,
        organization_id=org_id,
    )

    if base_query.count() == 0:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Nothing found!",
        )
        return None, exception

    # Apply dynamic filters based on parameters passed
    param = params.filter_parameter.value
    if param == "all":
        if params.filter_by_date and params.end_date and not params.start_date:
            # filter by date enabled
            # query all gifts by date created
            query = base_query.filter(Gift.created_at <= params.end_date)
        elif params.filter_by_date and params.start_date and params.end_date:
            query = base_query.filter(
                Gift.created_at >= params.start_date,
                Gift.created_at <= params.end_date,
            )

        else:
            # return all gifts
            query = base_query

    elif "purchased" in param or "reserved" in param:
        # query purchased or reserved gifts by date updated

        if params.filter_by_date and params.end_date and not params.start_date:
            query = base_query.filter(
                Gift.gift_status == param,
                Gift.updated_at <= params.end_date,
            )

        elif params.filter_by_date and params.start_date and params.end_date:
            query = base_query.filter(
                Gift.gift_status == param,
                Gift.updated_at >= params.start_date,
                Gift.updated_at <= params.end_date,
            )
        elif params.start_date and not params.end_date:
            query = base_query.filter(Gift.created_at >= params.start_date)

        else:
            query = base_query.filter(Gift.gift_status == param)

    else:
        # if not all, if not purchased nor reserved, and
        # no specified date query gifts based on the param
        # this block is for future purpose, in case more param are needed
        query = base_query.filter(Gift.gift_status == param)

    # Execute the final query
    gifts = query.all()

    if not gifts:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"No gifts found under {param} category"
            f" or specified date",
        )
        return None, exception

    # return a custom response
    response = CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Gifts retrieved successfully",
        data=jsonable_encoder(gifts, exclude=["organization"]),
    )
    return response, None


def add_cash_gift(
    org_id: str,
    gift_item: AddCashGift,
    db: Session,
) -> CustomResponse:
    """Add Cash funds gift to the organization.

    Args:
        gift_item (Dict): The gift data to be added.
        db (Session): The database session.
    Returns:
        raise an exception
        return a CustomResponse
    """

    cash_gift_item = gift_item.model_dump(exclude=["payment_options"])
    cash_gift_item["organization_id"] = org_id

    new_gift = Gift(**cash_gift_item, id=uuid4().hex)

    try:
        db.add(new_gift)
        db.commit()
        db.refresh(new_gift)

        for option in gift_item.payment_options:
            payment_option = PaymentOption(
                **option.__dict__,
                id=uuid4().hex,
                gift_id=new_gift.id,
            )
            db.add(payment_option)
            db.commit()
            db.refresh(payment_option)
            # commit and refresh again to return payment options
            db.commit()
            db.refresh(new_gift)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Gift successfully added",
            data=jsonable_encoder(new_gift, exclude=["organization"]),
        )
    except Exception as exc:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to add gift",
        ) from exc


def edit_cash_gift(
    gift_id: str,
    gift_item: EditCashGift,
    db: Session,
) -> CustomResponse:
    """Edit Cash funds gift.

    Args:
        gift_id,
        gift_item (Dict): The gift data to be updated,
        db (Session): The database session.

    Returns:
        raise an exception
        return a CustomResponse
    """
    # Check if gift exists
    gift_instance = db.query(Gift).filter(Gift.id == gift_id).first()
    if not gift_instance:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Gift not found",
            data={"gift_id": gift_id},
        )

    update_cash_item = gift_item.model_dump(exclude=["payment_options"])
    update_options = (
        db.query(PaymentOption)
        .filter(PaymentOption.gift_id == gift_id)
        .first()
    )

    try:
        for key, value in update_cash_item.items():
            setattr(gift_instance, key, value)
        db.commit()
        db.refresh(gift_instance)

        for key, value in gift_item.payment_options.__dict__.items():
            setattr(update_options, key, value)
        db.commit()
        db.refresh(update_options)

        # commit and refresh again to return updated details
        db.commit()
        db.refresh(gift_instance)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Gift successfully added",
            data=jsonable_encoder(gift_instance, exclude=["organization"]),
        )
    except Exception as exc:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update gift",
        ) from exc
