from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base_crud import CRUDBase
from app.models.survey_model import Survey
from app.models.user_model import User
from app.models.response_model import Response
from app.schemas.survey_schema import SurveyCreate, SurveyUpdate
from app.utils.exceptions import SurveyNotFoundException


class CRUDSurvey(CRUDBase[Survey, SurveyCreate, SurveyUpdate]):
    async def create_survey(self, *, obj_in: SurveyCreate, db: AsyncSession, current_user: User):
        db_survey = Survey(**obj_in.model_dump())
        db_survey.creator_id = current_user.id
        try:
            db.add(db_survey)
            await db.commit()
            await db.refresh(db_survey)
        except IntegrityError:
            await db.rollback()
        return db_survey

    async def get_survey(self, *, survey_id: int, db: AsyncSession):
        survey_in_db = await self.get(db=db, id=survey_id)
        if not survey_in_db:
            raise SurveyNotFoundException
        return survey_in_db

    async def get_surveys(self, *, skip: int = 0, limit: int = 100, db: AsyncSession):
        stmt = select(Survey).offset(skip).limit(limit)
        result = await db.execute(stmt)
        surveys = result.scalars().all()
        return surveys

    async def get_user_surveys(self, *, skip: int = 0, limit: int = 100, db: AsyncSession, current_user: User):
        stmt = select(Survey).where(Survey.creator_id == current_user.id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        surveys = result.scalars().all()
        return surveys

    async def get_survey_with_responses(self, *, survey_id: int, db: AsyncSession):
        stmt = (
            select(Survey)
            .options(selectinload(Survey.questions), selectinload(Survey.responses).selectinload(Response.answers))
            .where(Survey.id == survey_id)
        )
        result = await db.execute(stmt)
        surveys_with_responses = result.scalar_one_or_none()
        if not surveys_with_responses:
            raise SurveyNotFoundException
        return surveys_with_responses

    async def update_survey(self, *, survey_id: int, obj_in: SurveyUpdate, db: AsyncSession) -> Survey:
        survey_in_db = await self.get_survey(db=db, survey_id=survey_id)
        return await self.update(obj_current=survey_in_db, obj_in=obj_in, db=db)

    async def delete_survey(self, *, survey_id: int, db: AsyncSession):
        return await self.delete(db=db, id=survey_id)


survey = CRUDSurvey(Survey)
