"""This module provides functions for handling registry/gift related
operations."""


from typing import Any, Dict

import cloudinary
import cloudinary.api
import cloudinary.uploader
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomException, CustomResponse
from app.core.config import settings
from app.services.organization_services import check_organization_exists

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
).signature_algorithm = "sha256"


def upload_file_to_cloudinary(
    file: UploadFile, organization_id: str, db: Session
) -> CustomResponse:
    """Upload a file to cloudinary.

    Args:
        file (UploadFile): The file to be uploaded.
        organization_id (str): The id of the organization.
        db (Session): The database session.

    Raises:
        CustomException: Raised if the organization does not exist.

    Returns:
        CustomResponse: The response for the uploaded file.

    Examples:
        ```python
        from fastapi import FastAPI, File, UploadFile
        from sqlalchemy.orm import Session

        from app.api.responses.custom_responses import CustomResponse
        from app.services.file_services import upload_file_to_cloudinary
        from app.database.connection import get_db

        app = FastAPI()

        @app.post("/upload")
        async def upload_file(organization_id:str, file: UploadFile =\
              File(...), db: Session = Depends(get_db)) -> CustomResponse:
            return upload_file_to_cloudinary(file=file, \
                organization_id="organization_id", db=db)
        ```
    """

    if check_organization_exists(db, organization_id=organization_id) is None:
        raise CustomException(
            status_code=404, message="Organization not found"
        )
    result: Dict[str, Any] = cloudinary.uploader.upload(
        file.file,
        folder=organization_id,
        resource_type="auto",
        overwrite=True,
        tags=[file.filename],
    )

    return CustomResponse(
        status_code=201,
        message="File uploaded successfully",
        data=result.get("secure_url"),
    )
