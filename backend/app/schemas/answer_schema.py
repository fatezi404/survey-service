from pydantic import BaseModel, ConfigDict


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AnswerBase(OrmBaseModel):
    response_id: int
    question_id: int
    value: str | None = None
    option_id: int | None = None


class AnswerCreate(OrmBaseModel):
    value: str | None = None
    option_id: int | None = None


class AnswerUpdate(OrmBaseModel):
    value: str | None = None
    option_id: int | None = None


class AnswerResponse(AnswerBase):
    id: int
