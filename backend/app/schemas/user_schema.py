from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.role_schema import RoleDetails
from app.schemas.permission_schema import PermissionResponse

class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserBase(OrmBaseModel):
    email: EmailStr
    username: str = Field(
        min_length=3,
        max_length=36,
        pattern=r"^[a-zA-Z0-9]{3,36}$",
        description='Username must be 3-36 characters long and contain only letters and numbers'
    )


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_validator(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserUpdate(UserBase):
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = None


class UserPasswordUpdate(OrmBaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def password_validator(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserDetails(UserResponse):
    roles: list[RoleDetails] = []
    direct_permissions: list[PermissionResponse] = []


class UserLogin(OrmBaseModel):
    identifier: str
    password: str
