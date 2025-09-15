from pydantic import BaseModel, ConfigDict


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OptionBase(OrmBaseModel):
    question_id: int
    text: str


class OptionCreate(OptionBase):
    pass


class OptionCreateBulk(OrmBaseModel):
    options: list[OptionCreate]


class OptionUpdate(OrmBaseModel):
    text: str | None = None


class OptionResponse(OptionBase):
    id: int
