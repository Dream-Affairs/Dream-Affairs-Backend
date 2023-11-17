from fastapi import APIRouter, Depends

from app.api.models.role_permission_models import Permission
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.invite_schemas import RoleCreate
from app.database.connection import get_db
from app.services.custom_services import model_to_dict
from app.services.roles_services import get_all_roles, get_role_details, create_new_role

router = APIRouter(tags=["Roles & Permissions"])


@router.get("/permissions")
async def get_permissions(db=Depends(get_db)):
    permissions = model_to_dict(db.query(Permission).all())
    return CustomResponse(
        status_code=200,
        message="Permissions retrieved successfully",
        data=permissions,
    )


@router.get("/roles/{organization_id}")
async def get_roles(organization_id: str, db=Depends(get_db)):
    try:
        roles = get_all_roles(db, organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Roles retrieved successfully",
        data=roles,
    )


@router.get("/roles/{organization_id}/{role_id}")
async def get_role_by_id(organization_id: str, role_id: str, db=Depends(get_db)):
    try:
        role_details = get_role_details(db, organization_id, role_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Role retrieved successfully",
        data=role_details,
    )


@router.post("/roles")
async def create_role(role: RoleCreate, db=Depends(get_db)):
    try:
        role_details = create_new_role(db, role)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Role created successfully",
        data=role_details,
    )
