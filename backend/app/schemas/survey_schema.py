from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question_schema import QuestionResponse
from app.schemas.response_schema import ResponseResponse


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SurveyBase(OrmBaseModel):
    title: str = Field(min_length=3, max_length=64)
    description: str | None = None
    created_at: datetime
    creator_id: int
    is_active: bool
    deleted_at: datetime | None = None


class SurveyCreate(OrmBaseModel):
    title: str = Field(min_length=3, max_length=64)
    description: str | None = None


class SurveyResponse(SurveyBase):
    id: int


class SurveyUpdate(OrmBaseModel):
    title: str | None = None
    description: str | None = None


class SurveyDetails(SurveyResponse):
    questions: list[QuestionResponse]


class SurveyDetailsWithResponses(SurveyDetails):
    responses: list[ResponseResponse]
