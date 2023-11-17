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
from app.core.config import settings

account_name = settings.ACCOUNT_NAME
account_key = settings.KEY
connection_string = settings.CONNECTION_STRING


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


def create_blob(container_name: str, raw_file: UploadFile) -> str:
    """Create a Blob on azure
    Args:
        container_name: used to create a container if\
            it doesn't exists
        raw_file: the file to save as blob
    Return:
        Return the url to the blob on azure
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

    return blob_url


def add_product_gift(
    product_data: dict[str, Any],
    gift_image: UploadFile,
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
    authenticate_member = (
        db.query(Organization).filter(Organization.owner == member_id).first()
    )

    if not authenticate_member:
        exception = CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Invalid Owner"
        )
        return None, exception

    org_id = authenticate_member.id

    # upload a blob and retrieve the url
    image_file_path = create_blob(org_id, gift_image)

    # product_data = gift.model_dump()
    product_data["organization_id"] = org_id
    product_data["product_image_url"] = image_file_path

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

    except InternalError as e:
        print(e)
        db.rollback()
        exception = CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to add gift",
        )

        return None, exception
