""""This module contains functions that are used to process file imports."""
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.models.account_models import Account
from app.api.models.file_models import FailedFileImports, File, FileImports
from app.api.models.guest_models import Guest, GuestTags
from app.api.models.organization_models import OrganizationTag
from app.core.config import settings
from app.database.connection import SessionLocal
from app.services.custom_services import generate_rows

FILE_HEADER = [
    "first_name",
    "last_name",
    "email",
    "phone_number",
    "address",
    "city",
    "state",
    "zip",
    "country",
    "tags",
]


def fetch_file_import(file_import_id: str, db: Session) -> FileImports:
    """Fetches a file import from the database."""
    file_import = (
        db.query(FileImports)
        .filter(
            FileImports.file_id == file_import_id,
            FileImports.in_progress.is_(False),
            FileImports.current_line == 0,
        )
        .first()
    )

    return file_import


def update_current_line(
    file_import_id: str, current_line: int, db: Session
) -> None:
    """This function updates the file instance in the db to keep track of where
    it has gotten to in the file."""

    file_import = (
        db.query(FileImports).filter(FileImports.id == file_import_id).first()
    )
    file_import.current_line = current_line
    db.commit()


def log_import_error(
    import_id: str, error: str, line: str, db: Session
) -> None:
    """This function tracks all the errors that happen while importing a
    file."""
    failed_import = FailedFileImports(
        error=error, import_id=import_id, line=line
    )
    db.add(failed_import)
    db.commit()


def update_import_status(import_id: str, db: Session) -> None:
    """This function updates the import instance if it is done or not."""
    file_import = (
        db.query(FileImports).filter(FileImports.id == import_id).first()
    )
    file_import.in_progress = False
    db.commit()


def check_tags(tags: list, organization_id: str, db: Session) -> list:
    """This function keeps track of tags that are being added to the
    organization."""
    # check if tags exist in the organization
    tag_list = []
    print("starting tag check...")
    if not tags:
        return tag_list
    for tag in tags:
        tag_instance = (
            db.query(OrganizationTag)
            .filter(
                OrganizationTag.organization_id == organization_id,
                OrganizationTag.name == tag,
            )
            .first()
        )
        if tag_instance:
            print("tag found")
            tag_list.append(tag_instance.id)
        else:
            print("tag not found")
            tag_id = uuid4().hex
            tag_instance = OrganizationTag(
                id=tag_id,
                organization_id=organization_id,
                name=tag,
                tag_type="guest",
            )

            db.add(tag_instance)
            db.commit()
            db.refresh(tag_instance)
            tag_list.append(tag_instance.id)

    return tag_list


def validate_row(row: Dict[str, Any], line_no: int) -> bool:
    """This function validates the data in the row."""
    # validate row

    for key in FILE_HEADER:
        # Check if key exists in row
        if key not in row:
            return False, f"Missing {key} in line: {line_no}"

        # Validate email
        if key == "email":
            if "@" not in row[key] or "." not in row[key]:
                return False, f"Invalid email: {row[key]}"

        # Check if 'tags' is a list
        if key == "tags" and not isinstance(row[key], list):
            return False, f"Tags must be a list: {row[key]}"

    return True, ""


# pylint: disable=too-many-statements
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def process_start(import_id: str):
    """This function processes the file import."""
    with SessionLocal() as db:
        print("file processing starts...")

        file_import = fetch_file_import(import_id.strip('"'), db)

        if file_import.in_progress:
            # pass id to check_status function
            return {"message": "Import already in progress"}

        file: File = file_import.file
        file_path = f"{settings.IMPORT_DIR}/{file.file_name}"

        file_import.in_progress = True
        db.commit()
        print("file import marked in progress")

        counter = 0
        for row in generate_rows(file_path, file.file_type):
            if counter == 0:
                counter += 1

            print("formatting tags...")
            row["tags"] = row.get("tags").strip("][").split(", ")

            print("validating data...")
            valid, err = validate_row(row, counter)

            if not valid:
                log_import_error(file_import.id, err, counter, db)
                counter += 1
                update_current_line(file_import.id, counter, db)
                continue

            print("attempting to add guest")
            tags = check_tags(row["tags"], file.organization_id, db)
            if len(tags) == 0:
                log_import_error(
                    file_import.id,
                    "No valid tags found",
                    counter,
                    db,
                )
                counter += 1
                update_current_line(file_import.id, counter, db)
                continue
            print("tags checked")

            location = concatenate_address(
                row.get("address", ""),
                row.get("city", ""),
                row.get("state", ""),
                row.get("zip", ""),
                row.get("country", ""),
            )
            print("location concatenated")

            print("checking if guest email exists...")
            guest = (
                db.query(Guest)
                .filter(
                    Guest.email == row["email"],
                    Guest.organization_id == file.organization_id,
                )
                .first()
            )
            if guest:
                print("guest email exists")
                log_import_error(
                    file_import.id,
                    f"Guest with email {row['email']} already exists",
                    counter,
                    db,
                )
                counter += 1
                update_current_line(file_import.id, counter, db)
                continue
            print("check if email exist in account")
            is_account = (
                db.query(Account).filter(Account.email == row["email"]).first()
            )

            print("creating guest instance...")
            guest_id = uuid4().hex
            first_name = (
                is_account.first_name
                if is_account
                else row.get("first_name", None)
            )

            if first_name is None or first_name == "":
                log_import_error(
                    file_import.id,
                    f"First name is required for guest with email \
                        {row['email']}",
                    counter,
                    db,
                )
                counter += 1
                update_current_line(file_import.id, counter, db)
                continue

            last_name = (
                is_account.last_name
                if is_account and is_account.last_name != ""
                else row["last_name"]
            )

            guest_instance = Guest(
                id=guest_id,
                first_name=first_name,
                last_name=last_name,
                email=row["email"],
                phone_number=row["phone_number"],
                location=location,
                organization_id=file.organization_id,
            )

            print("guest instance created")
            print("adding guest tags...")

            for tag in tags:
                guest_tags = GuestTags(
                    id=uuid4().hex, guest_id=guest_id, tag_id=tag
                )
                db.add(guest_tags)

            print("adding guest to db...")

            try:
                db.add(guest_instance)
                db.commit()
                db.refresh(guest_instance)
                print("guest added to db")

            except SQLAlchemyError as e:
                print(e)
                log_import_error(file_import.id, str(e), counter, db)

            finally:
                counter += 1
                update_current_line(file_import.id, counter, db)
                continue
        return {"message": "File processed successfully"}


def concatenate_address(*args) -> str:
    """This function concatenates the address fields."""
    #  check if any of the address fields is empty
    print("concatenating address...")
    return ", ".join([arg for arg in args if arg != ""])
