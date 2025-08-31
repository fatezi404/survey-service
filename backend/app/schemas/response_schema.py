from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ResponseBase(OrmBaseModel):
    survey_id: int
    user_id: int | None = None
    submitted_at: datetime


class ResponseCreate(ResponseBase):
    pass


class ResponseUpdate(ResponseBase):
    pass # ??


class ResponseResponse(ResponseBase):
    id: int
