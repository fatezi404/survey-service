from pydantic import BaseModel, ConfigDict

from app.schemas.user_schema import UserResponse


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TokenBase(OrmBaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class TokenResponse(OrmBaseModel):
    access_token: str
    refresh_token: str


class TokenResponseWithType(OrmBaseModel):
    access_token: str
    token_type: str
