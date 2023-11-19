"""This module provides functions for handling registry/gift related
operations."""


from typing import Any

from azure.storage.blob import BlobServiceClient, ContainerClient
from fastapi import UploadFile, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.gift_models import Gift
from app.api.models.organization_models import Organization
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import AddProductGift
from app.core.config import settings

account_name = settings.ACCOUNT_NAME
account_key = settings.KEY
connection_string = settings.CONNECTION_STRING


def fake_authenticate(member_id: str, db: Session) -> Any:
    """This functions tries to mimic auth for a user
    Arg:
    member_id: the ID to validate and authenticate
    db: the database session.
    Return: if Authenticated return the org_id which the user belong to,
        if fails, return False.
    """
    authenticate_member = (
        db.query(Organization).filter(Organization.owner == member_id).first()
    )
    if not authenticate_member:
        return False

    org_id = authenticate_member.id
    return org_id


def check_for_container(container_name: str) -> None:
    """Check if azure container exist
    Args:
        container_name: used for naming container\
        checks if container exists.
    Return: True or False
    """
    container = ContainerClient.from_connection_string(
        conn_str=connection_string, container_name=container_name
    )
    if not container.exists():
        container.create_container()


def create_blob(container_name: str, raw_file: UploadFile) -> tuple[Any, Any]:
    """Create a Blob on azure
    Args:
        container_name: used to create a container if
            it doesn't exists
        raw_file: the file to save as blob
    Return:
        Return a turple [None,Response] or [Response,None]
    """
    # check and create a container if not exist
    check_for_container(container_name)

    # process the file and upload blob
    blob_name = raw_file.filename
    blob_data = raw_file.file.read()
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )

    if not blob_client.exists():
        blob_client.upload_blob(blob_data)

        # the lines below is to meet up with max line length
    acct = account_name
    cont = container_name

    # general format for azure blob url
    blob_url = f"https://{acct}.blob.core.windows.net/{cont}/{blob_name}"

    response = CustomResponse(
        status_code=status.HTTP_201_CREATED,
        message="image uploaded successfully",
        data={"product_image_url": blob_url},
    )
    return response


def add_product_gift(
    gift: AddProductGift,
    member_id: str,
    db: Session,
) -> tuple[Any, Any]:
    """Add product gift to the associated authenticated user/organization.

    Args:
        product_data (Dict): The gift data to be added.

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


def edit_product_gift(
    gift_data: AddProductGift,
    gift_id: str,
    db: Session,
) -> tuple[Any, Any]:
    """Edit product gift  associated with user/organization.

    Args:
        gift_data (Dict): The gift data to be updated.
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

    product_data = gift_data.model_dump(exclude_unset=True)

    try:
        for key, value in product_data.items():
            setattr(gift_instance, key, value)
        db.commit()
        db.refresh(gift_instance)

        response = CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message="Gift successfully updated",
            data=jsonable_encoder(gift_instance),
        )
        return response, None

    except InternalError:
        db.rollback()
        exception = CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update gift",
        )

        return None, exception
