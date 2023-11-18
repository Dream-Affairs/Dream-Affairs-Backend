"""This module provides functions for handling registry/gift related
operations."""


from typing import Any

from azure.storage.blob import BlobServiceClient, ContainerClient
from fastapi import UploadFile, status
from fastapi.responses import Response

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
        settings.CONNECTION_STRING, container_name
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
        Return a tuple [None,Response] or [Response,None]
    """
    # check and create a container if not exist
    check_for_container(container_name)

    # process the file and upload blob
    blob_name = raw_file.filename
    blob_data = raw_file.file.read()

    blob_service_client = BlobServiceClient.from_connection_string(
        settings.CONNECTION_STRING
    )
    blob_client = blob_service_client.get_blob_client(
        container_name, blob_name
    )

    if not blob_client.exists():
        blob_client.upload_blob(blob_data)

    # general format for azure blob url
    blob_url = f"https://{settings.ACCOUNT_NAME}.blob.core.windows.net"
    blob_url += f"/{container_name}/{blob_name}"

    response = CustomResponse(
        status_code=status.HTTP_201_CREATED,
        message="image uploaded successfully",
        data={"product_image_url": blob_url},
    )
    return response


def fetch_blob(url: str) -> Response:
    """
    Fetch a blob from azure
    Args:
        url: the url of the blob
    Return:
        returns a response containing the blob
    """
    url_split = url.split("/")
    container_name = url_split[-2]
    blob_name = url_split[-1]
    blob_service_client = BlobServiceClient.from_connection_string(
        settings.CONNECTION_STRING
    )
    blob_client = blob_service_client.get_blob_client(
        container_name, blob_name
    )

    if not blob_client.exists():
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Blob not found"
        )

    return Response(
        content=blob_client.download_blob().readall(), media_type="image/png"
    )
