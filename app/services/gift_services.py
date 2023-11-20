"""This module provides functions for handling registry/gift related
operations."""

from datetime import datetime
from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.gift_models import Gift
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import AddProductGift, EditProductGift
from app.services.account_services import fake_authenticate


def add_product_gift(
    gift_item: AddProductGift,
    member_id: str,
    db: Session,
) -> tuple[Any, Any]:
    """Add product gift to the associated authenticated user/organization.

    Args:
        gift_item (Dict): The gift data to be added.

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

    gift_item = gift_item.model_dump()
    gift_item["organization_id"] = org_id

    new_gift = Gift(**gift_item)

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


def edit_product_gift(
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


def fetch_all_gifts(db: Session) -> tuple[Any, Any]:
    """Fetch all gifts that are not deleted.

    Args:
        db (Session): The database session.

    Returns:
        Tuple: [None,Exception] or [Response,Nonw]
    """

    gift_instance = (
        db.query(Gift).filter_by(is_deleted=False, is_gift_hidden=False).all()
    )

    if not gift_instance:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="No gifts found",
        )
        return None, exception

    response = CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Gifts retrieved successfully",
        data=jsonable_encoder(gift_instance, exclude=["organization"]),
    )
    return response, None
