"""This file contains the API routes for handling file operations."""
from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.database.connection import get_db
from app.services.file_services import upload_file_to_cloudinary

router = APIRouter(prefix="/file", tags=["Files"])


@router.post("/{organization_id}")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> Any:
    """Upload a gift image to cloud.

    Please note that you can only upload images of size less than 1MB.

    Args:
        organization_id (str): The id of the organization.
        file (UploadFile): The file to upload.

    Returns:
        url (str): The url of the uploaded file.
    """
    return upload_file_to_cloudinary(
        file=file, organization_id=auth.member.organization_id, db=db
    )
