"""Organization Guest Router."""


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.api.schemas.guest_schemas import AddGuest, UpdateGuest
from app.database.connection import get_db
from app.services.guest_services import (
    add_guest,
    fetch_all_guests,
    search_organization_guests,
    update_organization_guest,
)

router = APIRouter(
    prefix="/guests",
    tags=["Guests"],
)


@router.get("/all")
def get_guests(
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    get_guests:
        This method is used to get all the guests.

    Args:
        db: This is the SQLAlchemy Session object.
        skip: This is the number of guests to skip.
        limit: This is the number of guests to limit.

    Returns:
        List[Guest]: This is the list of guests.
    """
    return fetch_all_guests(
        db, auth.member.organization_id, kwargs={"skip": skip, "limit": limit}
    )


@router.post("/create")
def create_guest(
    guest: AddGuest,
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
):
    """
    create_guest:
        This method is used to create a guest.

    Args:
        db: This is the SQLAlchemy Session object.

    Returns:
        Guest: This is the guest that was created.
    """
    return add_guest(guest, auth.member.organization_id, db)


@router.get("/search")
def search_guests(
    email: str = "",
    name: str = "",
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    search_guests:
        This method is used to search the guests.

    Args:
        db: This is the SQLAlchemy Session object.
        skip: This is the number of guests to skip.
        limit: This is the number of guests to limit.

    Returns:
        List[Guest]: This is the list of guests.
    """
    return search_organization_guests(
        db,
        auth.member.organization_id,
        email,
        name,
        kwargs={"skip": skip, "limit": limit},
    )


# @router.post("/import")
# def import_guests(
#     file: UploadFile = File(...),
#     auth: Authorize = Depends(is_org_authorized),
#     db: Session = Depends(get_db),
# ):
#     """
#     import_guests:
#         This method is used to import the guests.

#     Args:
#         db: This is the SQLAlchemy Session object.

#     Returns:
#         List[Guest]: This is the list of guests.
#     """
#     return file


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


@router.put("/update/{guest_id}")
def update_guest(
    guest_id: str,
    guest: UpdateGuest,
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
    db: Session = Depends(get_db),
):
    """
    update_guest:
        This method is used to update a guest.

    Args:
        db: This is the SQLAlchemy Session object.

    Returns:
        Guest: This is the guest that was updated.
    """
    return update_organization_guest(guest_id, guest, db)
