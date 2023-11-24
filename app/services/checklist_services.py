"""This module contains the services for the checklist model."""

from datetime import datetime
from typing import Union
from uuid import uuid4

from sqlalchemy.orm import Session

from app.api.models.organization_models import Checklist
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


# def update_task():
#     ...


# def delete_task():
#     ...


# def get_task():
#     ...


# def get_all_tasks():
#     ...