"""This module contains the services for the checklist model."""

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import desc

from app.api.models.organization_models import Checklist
from app.api.responses.custom_responses import CustomException
from app.api.schemas.checklist_schemas import ChecklistResponse


def create_checklist(
    created_by: str,
    title: str,
    organization_id: str,
    db: Session,
    due_date: datetime | None = None,
    assigned_to: str | None = None,
    description: str | None = None,
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


def get_all_checklists(
    organization_id: str,
    member_id: str,
    status: str,
    sort_by: str,
    offset: int,
    limit: int,
    order: str,
    db: Session,
) -> Any:
    """Get all checklists."""
    query = db.query(Checklist).filter_by(organization_id=organization_id)

    if sort_by == "all":
        query = db.query(Checklist).filter_by(organization_id=organization_id)

    elif sort_by == "assigned_to_me":
        query = db.query(Checklist).filter_by(
            organization_id=organization_id, assigned_to=member_id
        )

    elif sort_by == "assigned_by_me":
        query = db.query(Checklist).filter_by(
            organization_id=organization_id, created_by=member_id
        )

    if status != "all":
        query = query.filter_by(status=status)

    total = query.count()

    # Order the query
    if order == "desc":
        query = query.order_by(desc(Checklist.created_at))
    else:
        query = query.order_by(Checklist.created_at)

    # Calculate total count before applying limit and offset
    total = query.count()

    # Initialize next_url and previous_url
    next_url = None
    previous_url = None

    # Apply limit and offset
    if total > 1:
        query = query.offset(offset).limit(limit)
        next_offset = offset + limit
        if next_offset < total:
            next_url = f"/checklist/{organization_id}/{member_id}?offset=\
{next_offset}&limit={limit}&sort_by={sort_by}&order={order}"
        if offset - limit >= 0:
            previous_url = f"/checklist/{organization_id}/{member_id}?offset=\
{offset - limit}&limit={limit}&sort_by={sort_by}&order={order}"

    # Fetch the data
    query = query.all()

    return {
        "total": total,
        "next_page_url": next_url,
        "previous_page_url": previous_url,
        "checklists": [
            {
                "id": checklist.id,
                "created_by": checklist.created_by,
                "assigned_to": checklist.assigned_to,
                "title": checklist.title,
                "description": checklist.description,
                "status": checklist.status,
                "due_date": checklist.due_date,
                "organization_id": checklist.organization_id,
                "created_at": checklist.created_at,
            }
            for checklist in query
        ],
    }
