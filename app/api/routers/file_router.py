"""This file contains the API routes for handling file operations."""
from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.file_services import upload_file_to_cloudinary

router = APIRouter(prefix="/file", tags=["Files"])


@router.post("/{organization_id}")
async def upload_file(
    organization_id: str,  # to be swapped with middleware
    file: UploadFile = File(...),
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
    return upload_file_to_cloudinary(
        file=file, organization_id=organization_id, db=db
    )
