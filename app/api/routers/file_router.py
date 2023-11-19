"""This file contains the API routes for handling file operations."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomException
from app.database.connection import get_db
from app.services.account_services import fake_authenticate
from app.services.file_services import create_blob, fetch_blob

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload-image")
async def upload_file(
    member_id: str,  # to be swapped with middleware
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
) -> Any:
    """Upload a gift image to cloud.

    Args:
        member_id: the id to authenticate the user
        gift_image: the file to use as gift image
        db: database session.

    Return: returns CustomResponse containing the product_image_url

    Exception:
        raises a CustomException if failed to create blob
    """
    # fake authenticate the user
    member_org_id = fake_authenticate(member_id, db)

    if not member_org_id:
        err = CustomException(
            status_code=status.HTTP_404_NOT_FOUND, message="Invalid member_id"
        )
        raise err

    response = create_blob(member_org_id, file)

    return response


@router.get("/get-image")
async def get_file(url: str) -> Any:
    """
    Fetch a blob from azure
    Args:
        url: the url of the blob
    Return:
        returns a response containing the blob
    """
    return fetch_blob(url)
