"""This module contains the checklist router."""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.checklist_schemas import ChecklistCreate
from app.database.connection import get_db
from app.services.checklist_services import create_checklist

router = APIRouter(
    prefix="/checklist",
    tags=["checklist"],
)


@router.post(
    "/create",
)
async def create_task(
    checklist: ChecklistCreate, db: Session = Depends(get_db)
) -> CustomResponse:
    """Create a task."""
    return CustomResponse(
        status_code=201,
        message="Task created successfully.",
        data=jsonable_encoder(
            create_checklist(
                created_by=checklist.created_by,
                assigned_to=checklist.assigned_to,
                title=checklist.title,
                organization_id=checklist.organization_id,
                due_date=checklist.due_date,
                db=db,
                description=checklist.description,
            )
        ),
    )
