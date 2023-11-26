"""This module contains the services for the checklist model."""

from datetime import datetime
from typing import Any, Dict, List, Union
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.models.organization_models import Checklist
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.checklist_schemas import ChecklistResponse


def create_checklist(
    created_by: str,
    assigned_to: str,
    title: str,
    organization_id: str,
    due_date: datetime,
    db: Session,
    description: Union[str, None] = None,
) -> ChecklistResponse:
    """Create a checklist.

    Args:
        created_by (str): The id of the user creating the checklist.
        assigned_to (str): The id of the user the checklist is assigned to.
        title (str): The title of the checklist.
        organization_id (str): The id of the organization the \
          checklist belongs to.
        due_date (datetime): The due date of the checklist.
        db (Session): The database session.
        description (Union[str, None], optional): The description \
          of the checklist. Defaults to None.

    Returns:
        ChecklistResponse: The response for the created checklist.
    """
    checklist_data = Checklist(
        id=uuid4().hex,
        created_by=created_by,
        assigned_to=assigned_to,
        title=title,
        due_date=due_date,
        description=description,
        status="pending",
        organization_id=organization_id,
    )

    db.add(checklist_data)
    db.commit()
    db.refresh(checklist_data)

    return ChecklistResponse(
        id=checklist_data.id,
        created_by=checklist_data.created_by,
        assigned_to=checklist_data.assigned_to,
        title=checklist_data.title,
        description=checklist_data.description,
        status=checklist_data.status,
        due_date=checklist_data.due_date,
        organization_id=checklist_data.organization_id,
        created_at=checklist_data.created_at,
    )


def update_checklist(
    checklist_id: str,
    db: Session,
    **kwargs: Dict[str, Any],
) -> ChecklistResponse:
    """Update a checklist."""
    checklist_instance = db.query(Checklist).filter_by(id=checklist_id).first()
    if checklist_instance:
        setattr(checklist_instance, "updated_at", datetime.utcnow())
        for key, value in kwargs.items():
            setattr(checklist_instance, key, value)
        db.commit()
        return ChecklistResponse(
            id=checklist_instance.id,
            created_by=checklist_instance.created_by,
            assigned_to=checklist_instance.assigned_to,
            title=checklist_instance.title,
            description=checklist_instance.description,
            status=checklist_instance.status,
            due_date=checklist_instance.due_date,
            organization_id=checklist_instance.organization_id,
            created_at=checklist_instance.created_at,
        )
    return CustomException(
        status_code=404,
        message="Checklist not found",
    )


def delete_checklist(
    checklist_id: str,
    db: Session,
) -> str:
    """Delete a checklist."""
    checklist_instance = db.query(Checklist).filter_by(id=checklist_id).first()
    if checklist_instance:
        db.delete(checklist_instance)
        db.commit()
        return ""
    return CustomException(
        status_code=404,
        message="Checklist not found",
    )


def get_checklist(
    checklist_id: str,
    db: Session,
) -> ChecklistResponse:
    """Get a checklist."""
    checklist_instance = db.query(Checklist).filter_by(id=checklist_id).first()
    if checklist_instance:
        data = ChecklistResponse(
            id=checklist_instance.id,
            created_by=checklist_instance.created_by,
            assigned_to=checklist_instance.assigned_to,
            title=checklist_instance.title,
            description=checklist_instance.description,
            status=checklist_instance.status,
            due_date=checklist_instance.due_date,
            organization_id=checklist_instance.organization_id,
            created_at=checklist_instance.created_at,
        )
        return CustomResponse(
            status_code=200,
            message="Checklist retrieved successfully",
            data=jsonable_encoder(data),
        )
    return CustomException(
        status_code=404,
        message="Checklist not found",
    )


def get_all_checklists(
    organization_id: str,
    db: Session,
) -> List[ChecklistResponse]:
    """Get all checklists."""
    checklist_instance = (
        db.query(Checklist).filter_by(organization_id=organization_id).all()
    )
    if checklist_instance:
        return [
            ChecklistResponse(
                id=checklist.id,
                created_by=checklist.created_by,
                assigned_to=checklist.assigned_to,
                title=checklist.title,
                description=checklist.description,
                status=checklist.status,
                due_date=checklist.due_date,
                organization_id=checklist.organization_id,
                created_at=checklist.created_at,
            )
            for checklist in checklist_instance
        ]
    return CustomException(
        status_code=404,
        message="No checklists found",
    )
