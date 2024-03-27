"""This module contains the services for the guest model."""

import secrets
import string
import uuid
from typing import List
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.models.guest_models import Guest, GuestTags
from app.api.models.organization_models import OrganizationTag
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.guest_schemas import (
    AddGuest,
    GuestAssignedTable,
    GuestMeal,
    GuestPlusOne,
    GuestResponse,
    GuestTagsSchema,
    UpdateGuest,
)


def add_guest(
    guest: AddGuest,
    organization_id: str,
    db: Session,
    rsvp_status: str = "pending",
) -> Guest:
    """Creates a guest.

    Args:
        guest (AddGuest): Guest to create
        organization_id (str): Organization ID
        db (Session): SQLAlchemy Session
        rsvp_status (str, optional): RSVP status. Defaults to "pending".

    Returns:
        Guest: Guest created
    """

    if db.query(Guest).filter(Guest.email == guest.email).first() is not None:
        raise CustomException(
            message="Guest with this email already exists",
            status_code=409,
        )

    guest_instance = Guest(
        id=uuid4().hex,
        first_name=guest.first_name,
        last_name=guest.last_name,
        email=guest.email,
        phone_number=guest.phone_number,
        location=guest.location,
        organization_id=organization_id,
        rsvp_status=rsvp_status,
        allow_plus_one=guest.allow_plus_one,
    )

    if guest.tags is not None:
        for tag in guest.tags:
            # check if tag is uuid

            try:
                uuid.UUID(tag)
            except ValueError as e:
                print(e)
                raise CustomException(
                    message="Invalid tag id",
                    status_code=400,
                ) from e
            if (
                db.query(OrganizationTag)
                .filter(OrganizationTag.id == tag)
                .first()
                is None
            ):
                continue
            db.add(
                GuestTags(
                    id=uuid4().hex,
                    guest_id=guest_instance.id,
                    tag_id=tag,
                )
            )

    if guest.table_group is not None:
        guest_instance.table_group = guest.table_group.table_group_id
        guest_instance.table_number = guest.table_group.table_number
        guest_instance.seat_number = guest.table_group.seat_number

    db.add(guest_instance)
    db.commit()
    db.refresh(guest_instance)

    # back_groung_tasks.add_task(
    #     send_invite_email,
    #     guest_instance.email,
    #     guest_instance.first_name,
    #     guest_instance.invite_code,
    # )

    return CustomResponse(
        message="Guest created successfully",
        data=GuestResponse(
            id=guest_instance.id,
            first_name=guest_instance.first_name,
            last_name=guest_instance.last_name,
            email=guest_instance.email,
            invite_code=guest_instance.invite_code,
            phone_number=guest_instance.phone_number,
            location=guest_instance.location,
            rsvp_status=guest_instance.rsvp_status,
            has_plus_one=guest_instance.has_plus_one,
            is_plus_one=guest_instance.is_plus_one,
            plus_one=GuestPlusOne(
                first_name=guest_instance.plus_one.first_name,
                last_name=guest_instance.plus_one.last_name,
                email=guest_instance.plus_one.email,
            )
            if guest_instance.plus_one
            else GuestPlusOne(),
            meal=GuestMeal(
                id=guest_instance.meal.id,
                name=guest_instance.meal.name,
            )
            if guest_instance.meal
            else GuestMeal(),
            table=GuestAssignedTable(
                table_group=guest_instance.table_group,
                table_number=guest_instance.table_number,
                seat_number=guest_instance.seat_number,
            )
            if guest_instance.table_group
            else GuestAssignedTable(),
            tag_ids=[
                GuestTagsSchema(
                    id=tag.tag_id,
                    name=tag.organization_tag.name,
                )
                for tag in guest_instance.guest_tags
                if tag != "string"
            ],
        ).model_dump(),
    )


def fetch_all_guests(
    db: Session, organization_id: str, **kwargs
) -> CustomResponse:
    """Fetches all guests.

    Args:
        db (Session): SQLAlchemy Session
        skip (int, optional): Number of guests to skip. Defaults to 0.
        limit (int, optional): Number of guests to limit. Defaults to 100.

    Returns:
        Dict[str, Any]: Guests fetched
    """
    guests = (
        db.query(Guest)
        .filter(Guest.organization_id == organization_id)
        .offset(kwargs.get("skip"))
        .limit(kwargs.get("limit"))
        .all()
    )

    return CustomResponse(
        message="Guests fetched successfully",
        data=[
            GuestResponse(
                id=guest.id,
                first_name=guest.first_name,
                last_name=guest.last_name,
                email=guest.email,
                invite_code=guest.invite_code,
                phone_number=guest.phone_number,
                location=guest.location,
                rsvp_status=guest.rsvp_status,
                has_plus_one=guest.has_plus_one,
                is_plus_one=guest.is_plus_one,
                plus_one=GuestPlusOne(
                    first_name=guest.plus_one.first_name,
                    last_name=guest.plus_one.last_name,
                    email=guest.plus_one.email,
                )
                if guest.plus_one
                else GuestPlusOne(),
                meal=GuestMeal(
                    id=guest.meal.id,
                    name=guest.meal.name,
                )
                if guest.meal
                else GuestMeal(),
                table=GuestAssignedTable(
                    table_group_id=guest.table_group,
                    table_number=guest.table_number,
                    seat_number=guest.seat_number,
                ),
                tag_ids=[
                    GuestTags(
                        id=tag.tag_id,
                        name=tag.organization_tag.name,
                    )
                    for tag in guest.guest_tags
                    if tag != "string"
                ],
            ).model_dump()
            for guest in guests
        ],
    )


def search_organization_guests(
    db: Session,
    organization_id: str,
    email: str = "",
    name: str = "",
    **kwargs,
) -> CustomResponse:
    """Searches guests.

    Args:
        db (Session): SQLAlchemy Session
        email (str, optional): Email to search. Defaults to "".
        name (str, optional): Name to search. Defaults to "".
        skip (int, optional): Number of guests to skip. Defaults to 0.
        limit (int, optional): Number of guests to limit. Defaults to 100.

    Returns:
        Dict[str, Any]: Guests searched
    """
    guests = db.query(Guest).filter(Guest.organization_id == organization_id)

    if email != "":
        guests = guests.filter(Guest.email.ilike(f"%{email}%"))
    if name != "":
        guests = guests.filter(
            or_(
                Guest.first_name.ilike(f"%{name}%"),
                Guest.last_name.ilike(f"%{name}%"),
            )
        )

    guests = guests.offset(kwargs.get("skip")).limit(kwargs.get("limit")).all()

    if len(guests) == 0:
        raise CustomException(
            message="No guests found", status_code=404, data=[]
        )
    return CustomResponse(
        message="Guests fetched successfully",
        data=[
            GuestResponse(
                id=guest.id,
                first_name=guest.first_name,
                last_name=guest.last_name,
                email=guest.email,
                invite_code=guest.invite_code,
                phone_number=guest.phone_number,
                location=guest.location,
                rsvp_status=guest.rsvp_status,
                has_plus_one=guest.has_plus_one,
                is_plus_one=guest.is_plus_one,
                plus_one=GuestPlusOne(
                    first_name=guest.plus_one.first_name,
                    last_name=guest.plus_one.last_name,
                    email=guest.plus_one.email,
                )
                if guest.plus_one
                else GuestPlusOne(),
                meal=GuestMeal(
                    id=guest.meal.id,
                    name=guest.meal.name,
                )
                if guest.meal
                else GuestMeal(),
                table=GuestAssignedTable(
                    table_group_id=guest.table_group,
                    table_number=guest.table_number,
                    seat_number=guest.seat_number,
                ),
                tag_ids=[
                    GuestTagsSchema(
                        id=tag.tag_id,
                        name=tag.organization_tag.name,
                    )
                    for tag in guest.guest_tags
                    if tag != "string"
                ],
            ).model_dump()
            for guest in guests
        ],
    )


def update_organization_guest(
    guest_id: str,
    guest: UpdateGuest,
    db: Session,
) -> CustomResponse:
    """Updates a guest.

    Args:
        guest_id (str): Guest ID
        guest (GuestPlusOne): Guest to update
        db (Session): SQLAlchemy Session

    Returns:
        Dict[str, Any]: Guest updated
    """
    guest_instance = db.query(Guest).filter(Guest.id == guest_id).first()

    if guest_instance is None:
        raise CustomException(
            message="Guest with this ID does not exist",
            status_code=404,
        )

    attributes = ["first_name", "last_name", "phone_number", "location"]

    for attr in attributes:
        if getattr(guest, attr) != "":
            setattr(guest_instance, attr, getattr(guest, attr))

    if guest.allow_plus_one:
        guest_instance.allow_plus_one = guest.allow_plus_one

    if guest.table_group is not None:
        guest_instance.table_group = guest.table_group.table_group_id
        guest_instance.table_number = guest.table_group.table_number
        guest_instance.seat_number = guest.table_group.seat_number

    if guest.tags is not None:
        add_tags(guest_id, guest.tags, db)

    db.commit()
    db.refresh(guest_instance)

    return CustomResponse(
        message="Guest updated successfully",
        data=GuestResponse(
            id=guest_instance.id,
            first_name=guest_instance.first_name,
            last_name=guest_instance.last_name,
            email=guest_instance.email,
            invite_code=guest_instance.invite_code,
            phone_number=guest_instance.phone_number,
            location=guest_instance.location,
            rsvp_status=guest_instance.rsvp_status,
            has_plus_one=guest_instance.has_plus_one,
            is_plus_one=guest_instance.is_plus_one,
            plus_one=GuestPlusOne(
                first_name=guest_instance.plus_one.first_name,
                last_name=guest_instance.plus_one.last_name,
                email=guest_instance.plus_one.email,
            )
            if guest_instance.plus_one
            else GuestPlusOne(),
            meal=GuestMeal(
                id=guest_instance.meal.id,
                name=guest_instance.meal.name,
            )
            if guest_instance.meal
            else GuestMeal(),
            table=GuestAssignedTable(
                table_group_id=guest_instance.table_group,
                table_number=guest_instance.table_number,
                seat_number=guest_instance.seat_number,
            ),
            tag_ids=[
                GuestTagsSchema(
                    id=tag.tag_id,
                    name=tag.organization_tag.name,
                )
                for tag in guest_instance.guest_tags
                if tag != "string"
            ],
        ).model_dump(),
    )


def generate_invite_code(db: Session, guest_id: str) -> str:
    """Generates an invite code for a guest.

    Args:
        db (Session): SQLAlchemy Session
        guest_id (str): Guest ID

    Returns:
        Dict[str, Any]: Invite code generated
    """
    guest = db.query(Guest).filter(Guest.id == guest_id).first()

    if guest is None:
        raise CustomException(
            message="Guest with this ID does not exist",
            status_code=404,
        )

    guest.invite_code = create_invite_code(guest.organization.name[:3])

    db.commit()
    db.refresh(guest)
    return "success"


#  function to generate unique 10 character code
def create_invite_code(prefix: str) -> str:
    """
    create_invite_code:
        This method is used to create an invite code.

    Args:
        prefix: This is the prefix for the invite code.

    Returns:
        str: This is the invite code.
    """

    code_gen = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(7)
    )
    return prefix + code_gen


def add_tags(guest_id, tags: List[str], db: Session):
    """
    add_tags:
        This method is used to add tags to a guest.

    Args:
        guest_id: This is the guest id.
        tags: This is the list of tags.
        db: This is the SQLAlchemy Session object.

    Returns:
        None
    """
    for i in tags:
        db.add(
            GuestTags(
                id=uuid4().hex,
                guest_id=guest_id,
                tag_id=i,
            )
        )
