from uuid import uuid4

from fastapi import APIRouter, Depends

from app.api.models.organization_models import OrganizationRole
from app.api.models.role_permission_models import Permission, RolePermission
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.invite_schemas import RoleCreate
from app.database.connection import get_db
from app.services.custom_services import model_to_dict
from app.services.roles_services import get_role_details, get_all_roles

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
    roles = get_all_roles(db, organization_id)
    return CustomResponse(
        status_code=200,
        message="Roles retrieved successfully",
        data=roles,
    )


@router.get("/roles/{organization_id}/{role_id}")
async def get_role_by_id(organization_id: str, role_id: str, db=Depends(get_db)):
    role_details = get_role_details(db, organization_id, role_id)
    return CustomResponse(
        status_code=200,
        message="Role retrieved successfully",
        data=role_details,
    )

@router.post("/roles")
async def create_role(role: RoleCreate, db=Depends(get_db)):
    new_role = OrganizationRole(
        name=role.name,
        description=role.description,
        organization_id=role.organization_id,
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    try:
        for permission in role.permissions:
            new_permission = RolePermission(
                id=uuid4().hex,
                organization_role_id=new_role.id,
                permission_id=permission,
            )
            print(new_permission.id)
            print(new_permission.organization_role_id)
            print(new_permission.permission_id)
            print("New Permission")
            db.add(new_permission)
            db.commit()
            db.refresh(new_permission)
    except Exception as e:
        return {"error": str(e)}

    return new_role
