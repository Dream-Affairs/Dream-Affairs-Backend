"""This file contains the API routes for handling file operations."""
from enum import Enum
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from python3_gearman import GearmanClient
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.file_schemas import FileResponse
from app.core.config import settings
from app.database.connection import get_db
from app.services.file_services import store_file, upload_file_to_cloudinary

G_CLIENT = GearmanClient([f"{settings.GEARMAN_HOST}:{settings.GEARMAN_PORT}"])


class FileFor(str, Enum):
    """This class represents the file for enum."""

    GUEST = "guest"


router = APIRouter(prefix="/file", tags=["Files"])


@router.post("")
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


@router.post("/import")
async def import_guests(
    file_for: FileFor,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
):
    """
    import_guests:
        This method is used to import the guests.

    Args:
        db: This is the SQLAlchemy Session object.

    Returns:
        List[Guest]: This is the list of guests.
    """
    file, error = await store_file(
        file=file,
        file_for=file_for,
        organization_id=auth.member.organization_id,
        user_id=auth.member.id,
        request_type="import",
        db=db,
        # background_task=background_tasks,
    )
    if error:
        raise error
    background_tasks.add_task(
        lambda: G_CLIENT.submit_job("imports", file.id, background=True)
    )
    return CustomResponse(
        message="File uploaded successfully",
        status_code=201,
        data=FileResponse(
            id=file.id,
            file_name=file.file_name,
            file_type=file.file_type,
            file_for=file_for,
            file_size=file.file_size,
            organization_id=file.organization_id,
            user_id=file.user_id,
            request_type=file.request_type,
            is_deleted=file.is_deleted,
            date_created=file.date_created,
        ).model_dump(),
    )


# @router.get("/download")
# async def download_file(
#     file_id: str,
#     db: Session = Depends(get_db),
#     auth: Authorize = Depends(is_org_authorized),
# ) -> Any:
#     """Download a file from cloudinary.

#     Args:
#         file_id (str): The id of the file to download.

#     Returns:
#         File: The file to download.
#     """
# return download_file_from_cloudinary(file_id=file_id, db=db)

# @router.get("example")

# @router.get("/export")
# def export_guests(
#     auth: Authorize = Depends(is_org_authorized),
#     db: Session = Depends(get_db),
# ):
#     """
#     export_guests:
#         This method is used to export the guests.

#     Args:
#         db: This is the SQLAlchemy Session object.

#     Returns:
#         List[Guest]: This is the list of guests.
#     """
#     return ""
