"""This module provides functions for handling registry/gift related
operations."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.gift_models import (
    BankDetail,
    Gift,
    LinkDetail,
    WalletDetail,
)
from app.api.models.organization_models import Organization
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import (
    AddProductGift,
    BankSchema,
    EditProductGift,
    FilterGiftSchema,
    LinkSchema,
    WalletSchema,
)
from app.services.account_services import fake_authenticate


def add_product_gift_(
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
    params: FilterGiftSchema,
    db: Session,
) -> tuple[Any, Any]:
    """Fetch all gifts that are not deleted and not hidden under a specified
    parameter based org_id provided.

    Args:
        params(FilterGiftSchema):
            org_id : str,
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
        is_deleted=False, is_gift_hidden=False, organization_id=params.org_id
    )

    if base_query.count() == 0:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid Org_id",
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


def add_bank_account(bank_details: BankSchema, db: Session) -> CustomResponse:
    """Add  bank detatils to the the organization provided.

    Args:
        bank_details(BankSchema):

        db (Session): The database session.

    Returns:
        return CustomeResponse
    """

    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == bank_details.organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": bank_details.organization_id},
        )

    bank_detail = bank_details.model_dump()

    # bankdetail base query
    bank_instance = db.query(BankDetail)

    if bank_instance.count() == 0:
        # automatically set as default, nothing in the db table
        bank_detail["is_default"] = True
        try:
            bank_data = BankDetail(**bank_detail, id=uuid4().hex)
            db.add(bank_data)
            db.commit()
            db.refresh(bank_data)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Added bank details successfully",
                data=jsonable_encoder(bank_data, exclude=["organization"]),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to add bank details",
                data={},
            ) from exception

    # check if default exist
    default_exist = bank_instance.filter_by(is_default=True).first()

    # check if default_exist and new data is to be default
    if default_exist and bank_details.is_default:
        try:
            # reset the default_exist
            default_exist.is_default = False
            db.commit()
            db.refresh(default_exist)

            # insert the new data
            bank_data = BankDetail(**bank_detail, id=uuid4().hex)
            db.add(bank_data)
            db.commit()
            db.refresh(bank_data)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Added bank details successfully",
                data=jsonable_encoder(bank_data, exclude=["organization"]),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to add bank details",
                data={},
            ) from exception

    # try to just add not as default
    try:
        bank_data = BankDetail(**bank_detail, id=uuid4().hex)
        db.add(bank_data)
        db.commit()
        db.refresh(bank_data)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Added bank details successfully",
            data=jsonable_encoder(bank_data, exclude=["organization"]),
        )

    except Exception as exception:
        raise CustomException(
            status_code=500,
            message="Failed to add bank details",
            data={},
        ) from exception


def add_wallet(wallet_details: WalletSchema, db: Session) -> CustomResponse:
    """Add  wallet detatils to the the organization provided.

    Args:
        wallet_details(WalletSchema):

        db (Session): The database session.

    Returns:
        return CustomeResponse
    """

    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == wallet_details.organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": wallet_details.organization_id},
        )

    wallet_detail = wallet_details.model_dump()

    # walletdetail base query
    wallet_instance = db.query(WalletDetail)

    if wallet_instance.count() == 0:
        # automatically set as default, if nothing in the db table
        wallet_detail["is_default"] = True
        try:
            wallet_data = WalletDetail(**wallet_detail, id=uuid4().hex)
            db.add(wallet_data)
            db.commit()
            db.refresh(wallet_data)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Added wallet details successfully",
                data=jsonable_encoder(wallet_data, exclude=["organization"]),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to add wallet details",
                data={},
            ) from exception

    # check if default exist
    default_exist = wallet_instance.filter_by(is_default=True).first()

    # check if default_exist and new data is to be default
    if default_exist and wallet_details.is_default:
        try:
            # reset the default_exist
            default_exist.is_default = False
            db.commit()
            db.refresh(default_exist)

            # insert the new data
            wallet_data = WalletDetail(**wallet_detail, id=uuid4().hex)
            db.add(wallet_data)
            db.commit()
            db.refresh(wallet_data)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Added wallet details successfully",
                data=jsonable_encoder(wallet_data, exclude=["organization"]),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to add wallet details",
                data={},
            ) from exception

    # try to just add not as default
    try:
        wallet_data = WalletDetail(**wallet_detail, id=uuid4().hex)
        db.add(wallet_data)
        db.commit()
        db.refresh(wallet_data)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Added wallet details successfully",
            data=jsonable_encoder(wallet_data, exclude=["organization"]),
        )

    except Exception as exception:
        raise CustomException(
            status_code=500,
            message="Failed to add wallet details",
            data={},
        ) from exception


def add_payment_link(link_details: LinkSchema, db: Session) -> CustomResponse:
    """Add  link detatils to the the organization provided.

    Args:
        link_details(LinkSchema):

        db (Session): The database session.

    Returns:
        return CustomeResponse
    """

    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == link_details.organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": link_details.organization_id},
        )

    link_detail = link_details.model_dump()

    # linkdetail base query
    link_instance = db.query(LinkDetail)

    if link_instance.count() == 0:
        # automatically set as default, if nothing in the db table
        link_detail["is_default"] = True
        try:
            link_data = LinkDetail(**link_detail, id=uuid4().hex)
            db.add(link_data)
            db.commit()
            db.refresh(link_data)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Added payment link details successfully",
                data=jsonable_encoder(link_data, exclude=["organization"]),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to add payment link details",
                data={},
            ) from exception

    # check if default exist
    default_exist = link_instance.filter_by(is_default=True).first()

    # check if default_exist and new data is to be default
    if default_exist and link_details.is_default:
        try:
            # reset the default_exist
            default_exist.is_default = False
            db.commit()
            db.refresh(default_exist)

            # insert the new data
            link_data = LinkDetail(**link_detail, id=uuid4().hex)
            db.add(link_data)
            db.commit()
            db.refresh(link_data)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Added payment link details successfully",
                data=jsonable_encoder(link_data, exclude=["organization"]),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to add payment link details",
                data={},
            ) from exception

    # try to just add not as default
    try:
        link_data = LinkDetail(**link_detail, id=uuid4().hex)
        db.add(link_data)
        db.commit()
        db.refresh(link_data)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Added payment link details successfully",
            data=jsonable_encoder(link_data, exclude=["organization"]),
        )

    except Exception as exception:
        raise CustomException(
            status_code=500,
            message="Failed to add payment link details",
            data={},
        ) from exception


def get_account(
    org_id: str,
    payment_id: str,
    payment_type: str,
    db: Session,
) -> CustomResponse:
    """Get a payment account.

    Args:
        org_id, payment_id, payment_type
        db (Session): The database session.

    Returns:
        return CustomeResponse
    """
    # Check if organization exists
    organization = (
        db.query(Organization).filter(Organization.id == org_id).first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": org_id},
        )

    if payment_type == "bank":
        payment_details = (
            db.query(BankDetail)
            .filter_by(organization_id=org_id, id=payment_id)
            .first()
        )
    elif payment_type == "wallet":
        payment_details = (
            db.query(WalletDetail)
            .filter_by(organization_id=org_id, id=payment_id)
            .first()
        )
    else:
        payment_details = (
            db.query(LinkDetail)
            .filter_by(organization_id=org_id, id=payment_id)
            .first()
        )

    if not payment_details:
        raise CustomException(
            status_code=404,
            message="Payment account not found",
            data={"payment_id": payment_id},
        )

    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Details retrieved successfully",
        data=jsonable_encoder(payment_details, exclude=["organization"]),
    )
