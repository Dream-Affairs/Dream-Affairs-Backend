"""This module contains the checklist router."""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.checklist_schemas import ChecklistCreate, ChecklistUpdate
from app.database.connection import get_db
from app.services.checklist_services import (
    create_checklist,
    delete_checklist,
    get_all_checklists,
    get_checklist,
    update_checklist,
)

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


@router.get("/get/{checklist_id}")
async def get_task(
    checklist_id: str, db: Session = Depends(get_db)
) -> CustomResponse:
    """Get a task."""
    return get_checklist(checklist_id, db)


@router.get("/get-all/{organization_id}")
async def get_all_tasks(
    organization_id: str, db: Session = Depends(get_db)
) -> CustomResponse:
    """Get all tasks."""
    return CustomResponse(
        status_code=200,
        message="Tasks retrieved successfully.",
        data=jsonable_encoder(get_all_checklists(organization_id, db)),
    )


@router.patch("/update/{checklist_id}")
async def update_task(
    checklist_id: str, req: ChecklistUpdate, db: Session = Depends(get_db)
) -> CustomResponse:
    """Update a task."""
    return update_checklist(
        checklist_id,
        db,
        **req.kwargs,
    )


@router.delete("/delete/{checklist_id}")
async def delete_task(
    checklist_id: str, db: Session = Depends(get_db)
) -> CustomResponse:
    """Delete a task."""
    return CustomResponse(
        status_code=200,
        message="Task deleted successfully.",
        data=jsonable_encoder(delete_checklist(checklist_id, db)),
    )
