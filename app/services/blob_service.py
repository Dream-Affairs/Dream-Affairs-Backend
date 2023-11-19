"""This Module provides a specific service for uploading files to the azure
blod server."""

import io

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from fastapi import UploadFile

from app.core.config import settings

# Retrieve the connection string from the settings
connection_string = settings.CONNECTION_STRING


def upload_image_to_azure_blob(
    container_name: str, uploaded_file: UploadFile, blob_name: str
) -> str | None:
    """Uploads an uploaded file to azure blob.

    Args:
        container_name : str - A category to store the images
        uploaded_file : UploadFile - The image that needs to be stored
          in Azure Blob Storage
        blob_name : str - Name of the image

    Returns:
        str: url of uploaded image

    Raises:
        Any exceptions that might occur during container creation or existence
            check.
    """
    try:
        # Create a blob service client
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )

        # Create a container if it doesn't exist
        container_client = blob_service_client.get_container_client(
            container_name
        )

        # Check if the container exists
        if not container_client.exists():
            container_client.create_container()

        # Upload the image to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )

        with io.BytesIO(uploaded_file.file.read()) as data:
            blob_client.upload_blob(data)

        # Construct the URL for accessing the image
        blob_url = f"{blob_client.url}"
        return blob_url

    except ResourceNotFoundError as not_found_err:
        print(f"Resource not found: {not_found_err}")
        # Handle the resource not found error
        return None
