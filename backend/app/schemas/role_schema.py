from pydantic import BaseModel, ConfigDict

from app.schemas.permission_schema import PermissionResponse

class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RoleBase(OrmBaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(OrmBaseModel):
    description: str | None = None


class RoleResponse(RoleBase):
    id: int


class RoleDetails(RoleResponse):
    permissions: list[PermissionResponse] = []
