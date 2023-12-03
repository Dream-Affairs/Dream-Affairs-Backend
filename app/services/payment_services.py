"""This module provides functions for handling payment related operations."""

from uuid import uuid4

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.models.gift_models import BankDetail, LinkDetail, WalletDetail
from app.api.models.organization_models import Organization
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import BankSchema, LinkSchema, WalletSchema


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


def get_accounts(
    org_id: str,
    filter_by: str,
    db: Session,
) -> CustomResponse:
    """Get  payment accounts.

    Args:
        org_id, filter_param
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

    # no handy solution to query and join 3 tables
    if filter_by == "all":
        payment_details = jsonable_encoder(
            (
                db.query(BankDetail)
                .filter(BankDetail.organization_id == org_id)
                .all()
            ),
            exclude=["organization"],
        )

        wallets = jsonable_encoder(
            (
                db.query(WalletDetail)
                .filter(WalletDetail.organization_id == org_id)
                .all()
            ),
            exclude=["organization"],
        )

        links = jsonable_encoder(
            (
                db.query(LinkDetail)
                .filter(LinkDetail.organization_id == org_id)
                .all()
            ),
            exclude=["organization"],
        )
        payment_details.extend(wallets)
        payment_details.extend(links)

    if filter_by == "default":
        payment_details = jsonable_encoder(
            (
                db.query(BankDetail)
                .filter_by(organization_id=org_id, is_default=True)
                .all()
            ),
            exclude=["organization"],
        )

        wallets = jsonable_encoder(
            (
                db.query(WalletDetail)
                .filter_by(organization_id=org_id, is_default=True)
                .all()
            ),
            exclude=["organization"],
        )

        links = jsonable_encoder(
            (
                db.query(LinkDetail)
                .filter_by(organization_id=org_id, is_default=True)
                .all()
            ),
            exclude=["organization"],
        )
        payment_details.extend(wallets)
        payment_details.extend(links)

    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Details retrieved successfully",
        data=payment_details,
    )


def update_bank(
    payment_id: str, bank_details: BankSchema, db: Session
) -> CustomResponse:
    """Update  bank detatils of the the organization provided.

    Args:
        bank_details(BankSchema):

        db (Session): The database session.

    Returns:
        return CustomeResponse
    """
    # query to update the data
    updated_details = (
        db.query(BankDetail).filter(BankDetail.id == payment_id).first()
    )
    if not updated_details:
        raise CustomException(
            status_code=404,
            message="Payment account not found",
            data={"payment_account_id": payment_id},
        )
    _data = bank_details.model_dump()

    # check if default exist
    default_exist = db.query(BankDetail).filter_by(is_default=True).first()

    # check if default_exist and new data is to be default
    if default_exist and bank_details.is_default:
        try:
            # reset the default_exist
            default_exist.is_default = False
            db.commit()
            db.refresh(default_exist)

            for key, value in _data.items():
                setattr(updated_details, key, value)
            db.commit()
            db.refresh(updated_details)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Updated bank details successfully",
                data=jsonable_encoder(
                    updated_details, exclude=["organization"]
                ),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to update bank details",
                data={},
            ) from exception

    # if no default set, just accept the update data
    try:
        for key, value in _data.items():
            setattr(updated_details, key, value)
        db.commit()
        db.refresh(updated_details)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Updated bank details successfully",
            data=jsonable_encoder(updated_details, exclude=["organization"]),
        )

    except Exception as exception:
        raise CustomException(
            status_code=500,
            message="Failed to update bank details",
            data={},
        ) from exception


def update_wallet(
    payment_id: str, wallet_details: WalletSchema, db: Session
) -> CustomResponse:
    """Update  wallet detatils of the the organization provided.

    Args:
        wallet_details(WalletSchema):

        db (Session): The database session.

    Returns:
        return CustomeResponse
    """
    # query to update the data
    updated_details = (
        db.query(WalletDetail).filter(WalletDetail.id == payment_id).first()
    )
    if not updated_details:
        raise CustomException(
            status_code=404,
            message="Payment account not found",
            data={"payment_account_id": payment_id},
        )
    _data = wallet_details.model_dump()

    # check if default exist
    default_exist = db.query(WalletDetail).filter_by(is_default=True).first()

    # check if default_exist and new data is to be default
    if default_exist and wallet_details.is_default:
        try:
            # reset the default_exist
            default_exist.is_default = False
            db.commit()
            db.refresh(default_exist)

            for key, value in _data.items():
                setattr(updated_details, key, value)
            db.commit()
            db.refresh(updated_details)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Updated wallet details successfully",
                data=jsonable_encoder(
                    updated_details, exclude=["organization"]
                ),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to update wallet details",
                data={},
            ) from exception

    # if no default set, just accept the update data
    try:
        for key, value in _data.items():
            setattr(updated_details, key, value)
        db.commit()
        db.refresh(updated_details)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Updated wallet details successfully",
            data=jsonable_encoder(updated_details, exclude=["organization"]),
        )

    except Exception as exception:
        raise CustomException(
            status_code=500,
            message="Failed to update wallet details",
            data={},
        ) from exception


def update_link(
    payment_id: str, link_details: LinkSchema, db: Session
) -> CustomResponse:
    """Update  link detatils of the the organization provided.

    Args:
        link_details(linkSchema):

        db (Session): The database session.

    Returns:
        return CustomeResponse
    """
    # query to update the data
    updated_details = (
        db.query(LinkDetail).filter(LinkDetail.id == payment_id).first()
    )
    if not updated_details:
        raise CustomException(
            status_code=404,
            message="Payment account not found",
            data={"payment_account_id": payment_id},
        )
    _data = link_details.model_dump()

    # check if default exist
    default_exist = db.query(LinkDetail).filter_by(is_default=True).first()

    # check if default_exist and new data is to be default
    if default_exist and link_details.is_default:
        try:
            # reset the default_exist
            default_exist.is_default = False
            db.commit()
            db.refresh(default_exist)

            for key, value in _data.items():
                setattr(updated_details, key, value)
            db.commit()
            db.refresh(updated_details)

            return CustomResponse(
                status_code=status.HTTP_201_CREATED,
                message="Updated link details successfully",
                data=jsonable_encoder(
                    updated_details, exclude=["organization"]
                ),
            )

        except Exception as exception:
            raise CustomException(
                status_code=500,
                message="Failed to update link details",
                data={},
            ) from exception

    # if no default set, just accept the update data
    try:
        for key, value in _data.items():
            setattr(updated_details, key, value)
        db.commit()
        db.refresh(updated_details)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Updated link details successfully",
            data=jsonable_encoder(updated_details, exclude=["organization"]),
        )

    except Exception as exception:
        raise CustomException(
            status_code=500,
            message="Failed to update link details",
            data={},
        ) from exception
