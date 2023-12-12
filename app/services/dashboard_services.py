"""This module defines the router for the dashboard endpoints."""
from sqlalchemy.orm import Session

from app.api.models.organization_models import Organization
from app.api.responses.custom_responses import CustomException


def get_org_user_dash(organization_id: str, db: Session):
    """Get the dashboard data for the user.

    Args:
        organization_id (str): Organization ID
        db (Session, optional): Database session. Defaults to Depends(get_db).
        auth (Authorize, optional): Authorization header. \
          Defaults to Depends(is_authenticated).

    Returns:
        CustomResponse: Dashboard data
    """
    organization_instance = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )
    if organization_instance is None:
        raise CustomException(
            status_code=401,
            message="Unauthorized",
        )
    return True
