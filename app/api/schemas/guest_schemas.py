"""Guest Pydantic models."""
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class GuestPlusOne(BaseModel):
    """

    Guest Plus One Model:
      This model is used to define the plus one for the guest.

    Attributes:
      first_name (str): The first name of the plus one.
      last_name (str): The last name of the plus one.
      email (EmailStr): The email of the plus one.

    """

    first_name: str = ""
    last_name: str = ""
    email: EmailStr = ""


class GuestMeal(BaseModel):
    """
    Guest Meal Model:
      This model is used to define the meal for the guest.

    Attributes:
      id (str): The id of the meal.
      name (str): The name of the meal.

    """

    id: str = ""
    name: str = ""


class GuestTagsSchema(BaseModel):
    """
    Guest Tags Schema:
      This schema is used to define the tags for the guest.

    Attributes:
      id (str): The id of the tag.
      name (str): The name of the tag.
    """

    id: str = ""
    name: str = ""


class GuestAssignedTable(BaseModel):
    """
    Guest Assigned Table:
      This model is used to define the assigned table for the guest.

    Attributes:
      table_group_id (str): The id of the table group.
      table_number (int): The number of the table.
      seat_number (int): The number of the seat.
    """

    table_group_id: Optional[str] = None
    table_number: int = 0
    seat_number: int = 0


class GuestResponse(BaseModel):
    """
    Guest Response Model:
      This model is used to define the response for the guest.

    Attributes:
      id (str): The id of the guest.
      first_name (str): The first name of the guest.
      last_name (str): The last name of the guest.
      email (str): The email of the guest.
      phone_number (str): The phone number of the guest.
      invite_code (str): The invite code of the guest.
      location (str): The location of the guest.
      rsvp_status (str): The rsvp status of the guest.
      has_plus_one (bool): The has plus one status of the guest.
      is_plus_one (bool): The is plus one status of the guest.
      plus_one (GuestPlusOne): The plus one of the guest.
      tag_ids (List[GuestTagsSchema]): The tag ids of the guest.
      table (GuestAssignedTable): The assigned table of the guest.
      meal (GuestMeal): The meal of the guest.
    """

    id: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone_number: str = ""
    invite_code: str = ""
    location: str = ""
    rsvp_status: str
    has_plus_one: bool
    is_plus_one: bool
    plus_one: GuestPlusOne
    tag_ids: List[GuestTagsSchema]
    table: GuestAssignedTable
    meal: GuestMeal


class AddGuest(GuestPlusOne):
    """
    Add Guest Model:
      This model is used to define the guest to add.

    Attributes:
      first_name (str): The first name of the guest.
      last_name (str): The last name of the guest.
      email (EmailStr): The email of the guest.
      phone_number (str): The phone number of the guest.
      location (str): The location of the guest.
      allow_plus_one (bool): The allow plus one status of the guest.
      table_group (GuestAssignedTable): The assigned table of the guest.
      tags (List[str]): The tags of the guest.
    """

    phone_number: Optional[str] = ""
    location: Optional[str] = ""
    allow_plus_one: bool = False
    table_group: Optional[GuestAssignedTable] = None
    tags: Optional[List[str]] = None


class UpdateGuest(BaseModel):
    """
    Update Guest Model:
      This model is used to define the guest to update.

    Attributes:
      first_name (str): The first name of the guest.
      last_name (str): The last name of the guest.
      phone_number (str): The phone number of the guest.
      location (str): The location of the guest.
      allow_plus_one (bool): The allow plus one status of the guest.
      table_group (GuestAssignedTable): The assigned table of the guest.
      tags (List[str]): The tags of the guest.
    """

    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    phone_number: Optional[str] = ""
    location: Optional[str] = ""
    allow_plus_one: Optional[bool] = False
    table_group: Optional[GuestAssignedTable] = None
    tags: Optional[List[str]] = None
