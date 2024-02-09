"""This module defines the router for the role endpoints."""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm.session import Session

from app.api.middlewares.authorization import (
    Authorize,
    is_authenticated,
    is_org_authorized,
)
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.organization_schemas import (
    InviteMemberSchema,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.database.connection import get_db
from app.services.organization_services import (
    accept_invite,
    create_organization,
    delete_organization,
    get_all_organizations,
    get_members,
    get_organization,
    invite_member,
    resend_invite,
    suspend_member,
    update_organization_details,
)

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("")
async def create_user_organization(
    req: OrganizationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """# Create an organization.

    This endpoint creates an organization and assigns the authenticated
    user as the owner.

    ## Args:

    - req `(OrganizationCreate)`: Organization details
    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).

    ## Returns:

    - `CustomResponse`: Organization details

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'POST'
    'http://localhost:8000/organization'
    -H 'accept: application/json'
    -H 'Content-Type: application/json'
    -d '{
    "name": "Organization Name",
    "description": "Organization Description"
    }'
    ```

    ## Response:

    ```json
    {
        "status_code": 201,
        "message": "Organization created successfully",
        "data": {
            "id": "organization_id",
            "name": "Organization Name",
            "description": "Organization Description",
            "owner_id": "owner_id"
        }
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Organization could not be created"
    }
    ```
    """
    try:
        organization_details = await create_organization(
            db, auth.account.id, req, background_tasks
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=201,
        message="Organization created successfully",
        data=organization_details,
    )


@router.get("/all")
async def get_all_user_organizations(
    db: Session = Depends(get_db),  # pylint: disable=unused-argument
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_authenticated
    ),
) -> CustomResponse:
    """# Get all organizations.

    This endpoint retrieves all organizations that the authenticated
    user is a member of.

    ## Args:

    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token

    ## Returns:

    - `CustomResponse`: List of organizations

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'GET'
    'http://localhost:8000/organization/all'
    -H 'accept: application/json'
    -H 'Authorization
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Organization retrieved successfully",
        "data": [
            {
                "id": "organization_id",
                "name": "Organization Name",
                "description": "Organization Description",
                "owner_id": "owner_id"
            }
        ]
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Organization could not be retrieved"
    }
    ```
    """
    return CustomResponse(
        status_code=200,
        message="Organization retrieved successfully",
        data=get_all_organizations(account_id=auth.account.id, db=db),
    )


@router.get("")
async def get_user_organization(
    db: Session = Depends(get_db),  # pylint: disable=unused-argument
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
):
    """# Get an organization.

    This endpoint retrieves an organization that the authenticated
    user is a member of.

    ## Args:

    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token
    - organization_id `(str)``[cookies]`: Organization ID

    ## Returns:

    - `CustomResponse`: Organization details

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'GET'
    'http://localhost:8000/organization'
    -H 'accept: application/json'
    -H 'Authorization
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Organization retrieved successfully",
        "data": {
            "id": "organization_id",
            "name": "Organization Name",
            "description": "Organization Description",
            "owner_id": "owner_id"
        }
    }

    ```
    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Organization could not be retrieved"
    }
    ```
    """
    return CustomResponse(
        status_code=200,
        message="Organization retrieved successfully",
        data=get_organization(
            db,
            auth.member.organization_id,
        ),
    )


@router.put("")
async def update_user_organization(
    req: OrganizationUpdate,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """# Update an organization.

    This endpoint updates an organization that the authenticated
    user is a member of.

    ## Args:

    - req `(OrganizationUpdate)`: Organization details
    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token

    ## Returns:

    - `CustomResponse`: Organization details

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'PUT'
    'http://localhost:8000/organization'
    -H 'accept: application/json'
    -H 'Content-Type: application/json'
    -H 'Authorization'
    -d '{
    "name": "Organization Name",
    "description": "Organization Description"
    }'
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Organization updated successfully",
        "data": {
            "id": "organization_id",
            "name": "Organization Name",
            "description": "Organization Description",
            "owner_id": "owner_id"
        }
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Organization could not be updated"
    }
    ```
    """
    try:
        organization_details = update_organization_details(db, req, auth)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Organization updated successfully",
        data=organization_details,
    )


@router.delete("")
async def delete_user_organization(
    background_tasks: BackgroundTasks,
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """
    NOTE: This endpoint is not recommended for use in production.
    # Delete an organization.

    This endpoint deletes an organization that the authenticated
    user is a member of.

    ## Args:

    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token
    - organization_id `(str)``[cookies]`: Organization ID

    ## Returns:

    - `CustomResponse`: Organization details

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'DELETE'
    'http://localhost:8000/organization'
    -H 'accept: application/json'
    -H 'Authorization
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Organization deleted successfully"
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Organization could not be deleted"
    }
    ```
    """

    if not delete_organization(
        db, auth.member.organization_id, background_tasks
    ):
        raise CustomException(
            status_code=400,
            message="Organization could not be deleted",
        )
    return CustomResponse(
        status_code=200,
        message="Organization deleted successfully",
    )


@router.post("/invite")
async def invite_new_member(
    invite: InviteMemberSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> CustomResponse:
    """# Invite a new member.

    This endpoint invites a new member to an organization.

    ## Args:

    - invite `(InviteMemberSchema)`: Invite details
    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token
    - organization_id `(str)``[cookies]`: Organization ID

    ## Returns:

    - `CustomResponse`: Invite details

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'POST'
    'http://localhost:8000/organization/invite'
    -H 'accept: application/json'
    -H 'Content-Type: application/json'
    -H 'Authorization'
    -d '{
    "name": "Name",
    "email": "example@email.com",
    "role_id": "role_id"
    }'
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Invite sent successfully",
        "data": {
            "id": "invite_id",
            "name": "Name",
            "email": "email",
            "role_id": "role_id"
        }
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Invite could not be sent"
    }
    ```
    """
    try:
        member_details = invite_member(
            db, invite, auth.member.organization_id, background_tasks
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invite sent successfully",
        data=member_details,
    )


@router.get("/members")
async def get_organization_members(
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> CustomResponse:
    """# Get organization members.

    This endpoint retrieves all members of an organization.

    ## Args:

    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token
    - organization_id `(str)``[cookies]`: Organization ID

    ## Returns:

    - `CustomResponse`: List of members

    ## Raises:

    - `CustomException`: If organization does not exist

    ## Example:

    ```curl
    curl -X 'GET'
    'http://localhost:8000/organization/members'
    -H 'accept: application/json'
    -H 'Authorization
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Members retrieved successfully",
        "data": [
            {
                "id": "member_id",
                "name": "Name",
                "email": "email",
                "role_id": "role_id"
            }
        ]
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Members could not be retrieved"
    }
    ```
    """
    try:
        invites = await get_members(db, auth.member.organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invites retrieved successfully",
        data=invites,
    )


# An endpoint to accept an invite
@router.get("/invite/accept/{invite_token}")
async def accept_invitation(
    invite_token: str,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Accept an invitation.

    This endpoint accepts an invitation to join an organization.

    ## Args:

    - invite_token `(str)`: Invite token
    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).

    ## Returns:

    - `CustomResponse`: Member details

    ## Raises:

    - `CustomException`: If token is invalid

    ## Example:

    ```curl
    curl -X 'GET'
    'http://localhost:8000/organization/invite/accept/invite_token'
    -H 'accept: application/json'
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Invite accepted successfully",
        "data": {
            "id": "member_id",
            "name": "Name",
            "email": "email",
            "role_id": "role_id"
        }
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Invite could not be accepted"
    }
    ```
    """
    try:
        member_details = accept_invite(db, invite_token)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invite accepted successfully",
        data=member_details,
    )


@router.get("/invite/{email}")
async def resend_invitation(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> CustomResponse:
    """# Resend an invitation.

    This endpoint resends an invitation to join an organization.

    ## Args:

    - email `(str)`: Email
    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token
    - organization_id `(str)``[cookies]`: Organization ID

    ## Returns:

    - `CustomResponse`: Invite details

    ## Raises:

    - `CustomException`: If token is invalid

    ## Example:

    ```curl
    curl -X 'GET'
    'http://localhost:8000/organization/invite/email'
    -H 'accept: application/json'
    -H 'Authorization
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Invite sent successfully",
        "data": {
            "id": "invite_id",
            "name": "Name",
            "email": "email",
            "role_id": "role_id"
        }
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Invite could not be sent"
    }
    ```
    """
    try:
        invite_details = resend_invite(
            db, email, auth.member.organization_id, background_tasks
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invite sent successfully",
        data=invite_details,
    )


@router.patch("/{member_id}")
async def suspend_unsuspend_membership(
    member_id: str,
    background_tasks: BackgroundTasks,
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Suspend a member.

    This endpoint suspends a member from an organization.

    ## Args:

    - member_id `(str)`: Member ID
    - db `(Session, optional)`: Database session. Defaults to Depends(get_db).
    - token `(str)`: Authentication token
    - organization_id `(str)``[cookies]`: Organization ID

    ## Returns:

    - `CustomResponse`: Member details

    ## Raises:

    - `CustomException`: If member does not exist

    ## Example:

    ```curl
    curl -X 'PATCH'
    'http://localhost:8000/organization/member_id'
    -H 'accept: application/json'
    -H 'Authorization
    ```

    ## Response:

    ```json
    {
        "status_code": 200,
        "message": "Member suspended successfully",
        "data": {
            "id": "member_id",
            "name": "Name",
            "email": "email",
            "role_id": "role_id"
        }
    }
    ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "message": "Member could not be suspended"
    }
    ```
    """
    try:
        member_details = suspend_member(
            db, auth.member.organization_id, member_id, background_tasks
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Member suspended successfully",
        data=member_details,
    )
