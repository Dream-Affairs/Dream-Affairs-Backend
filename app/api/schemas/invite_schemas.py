from pydantic import BaseModel, EmailStr


class RoleCreate(BaseModel):
    name: str
    description: str
    permissions: list[str]


class InviteOrgMember(BaseModel):
    email: EmailStr
    organization_id: str
    role: str
