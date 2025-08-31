from pydantic import BaseModel, ConfigDict

from app.schemas.option_schema import OptionResponse
from app.core.config import QuestionType


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class QuestionBase(OrmBaseModel):
    survey_id: int
    text: str
    type: QuestionType
    order: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(OrmBaseModel):
    text: str | None = None
    order: int | None = None


class QuestionResponse(QuestionBase):
    id: int


class QuestionDetails(QuestionResponse):
    options: list[OptionResponse]
