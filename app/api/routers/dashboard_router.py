"""This module defines the router for the dashboard endpoints."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_authenticated
from app.database.connection import get_db
from app.services.account_services import encode_data
from app.services.dashboard_services import get_org_user_dash

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{organization_id}")
async def get_organization_user_dashboard(
    organization_id: str,
    res: Response,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
):
    """Get the dashboard data for the user.

    Args:
        organization_id (str): Organization ID
        db (Session, optional): Database session. Defaults to Depends(get_db).
        auth (Authorize, optional): Authorization header. \
          Defaults to Depends(is_authenticated).

    Returns:
        CustomResponse: Dashboard data
    """
    res.set_cookie(
        "emxsidqw",
        encode_data(organization_id),
        httponly=True,
    )

    get_org_user_dash(organization_id, db)
    return {
        "message": "Dashboard data retrieved successfully",
        "data": {
            "account_id": auth.account.id,
            "account_email": auth.account.email,
            "account_first_name": auth.account.first_name,
            "account_last_name": auth.account.last_name,
        },
    }
