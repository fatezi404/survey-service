from typing import Any
from pydantic import BaseModel, ConfigDict


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PermissionBase(OrmBaseModel):
    name: str
    description: str | None = None
    resource: str
    action: str
    conditions: dict[str, Any] | None = None


class PermissionUpdate(OrmBaseModel):
    description: str | None = None
    resource: str | None = None
    action: str | None = None
    conditions: dict[str, Any] | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
