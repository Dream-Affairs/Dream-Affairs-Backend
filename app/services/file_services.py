"""This module provides functions for handling registry/gift related
operations."""

import os
from typing import Any, Dict
from uuid import uuid4

import cloudinary
import cloudinary.api
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from app.api.models.file_models import File, FileImports
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.core.config import settings
from app.services.custom_services import generate_rows
from app.services.organization_services import check_organization_exists

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
).signature_algorithm = settings.HASH_ALGORITHM


IMPORT_FOLDER = os.path.join(os.path.abspath(settings.IMPORT_DIR))


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


async def store_file(
    file: UploadFile,
    file_for: str,
    organization_id: str,
    user_id: str,
    request_type: str,
    db: Session,
    # background_task: BackgroundTasks,
) -> tuple[File, CustomException]:
    """Store the file in the database.

    Args:
        file_name (str): The name of the file.
        file_type (str): The type of the file.
        file_size (str): The size of the file.
        organization_id (str): The id of the organization.
        user_id (str): The id of the user.
        request_type (str): The type of request.
        db (Session): The database session.

    Returns:
        Tuple[File, CustomException]: The file object and the exception if any.

    Examples:

        ```python
        from fastapi import FastAPI, File, UploadFile
        from sqlalchemy.orm import Session

        from app.api.models.file_models import File
        from app.api.responses.custom_responses import CustomException
        from app.services.file_services import store_file
        from app.database.connection import get_db

        app = FastAPI()

        @app.post("/store")
        async def store_file(
            organization_id:str,
            user_id:str, request_type:str,
            file: UploadFile = File(...),
            db: Session = Depends(get_db)) -> Tuple[File, CustomException]:

            file, error = store_file(
                file=file,
                organization_id="organization_id",
                user_id="user_id",
                request_type="request_type",
                db=db
            )
            if err:
                raise err

            return file
        ```
    """

    # check if file type is allowed
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        return None, CustomException(
            status_code=400, message="File type not allowed"
        )

    file_path = store_file_in_import_folder(
        file=file, organization_id=organization_id
    )

    if file_path is None:
        return None, CustomException(
            status_code=500, message="Failed to store file"
        )

    file_type = ""
    if (
        file.content_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        file_type = "xlsx"

    else:
        file_type = "csv"

    file_id = uuid4().hex
    file = File(
        id=file_id,
        file_name=file_path.split("/")[-1],
        file_type=file_type,
        file_size=file.size,
        organization_id=organization_id,
        user_id=user_id,
        request_type=request_type,
        file_for=file_for,
        import_info=[
            FileImports(
                id=uuid4().hex,
                file_id=file_id,
                total_line=await count_rows(file_path, file_type),
                in_progress=False,
                user_id=user_id,
            )
        ],
    )

    db.add(file)

    try:
        db.commit()
        db.refresh(file)
        # background_task.add_task()
        return file, None
    except DataError as e:
        print(e)
        db.rollback()
        os.remove(file_path)
        return None, CustomException(
            status_code=500, message="Failed to store file"
        )
    except HTTPException:
        db.rollback()
        os.remove(file_path)
        return None, CustomException(
            status_code=500, message="Failed to store file"
        )


def store_file_in_import_folder(file: UploadFile, organization_id: str) -> str:
    """Store the file in the import folder."""
    file_name = file.filename.split(".")
    full_path = (
        IMPORT_FOLDER
        + "/"
        + file_name[0]
        + "_"
        + organization_id
        + "."
        + file_name[1]
    )
    try:
        with open(full_path, "wb") as f:
            f.write(file.file.read())
            f.close()
        return full_path
    except FileNotFoundError as e:
        print(e)
        return None


async def count_rows(filename: str, ftype: str) -> int:
    """This function counts the number of rows in a file."""
    num_rows = 0
    for _ in generate_rows(filename, ftype):
        num_rows += 1
    return num_rows
