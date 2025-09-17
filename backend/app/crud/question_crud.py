from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.question_model import Question
from app.crud.survey_crud import survey
from app.schemas.question_schema import QuestionCreate, QuestionUpdate
from app.utils.exceptions import QuestionNotFoundException


class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionUpdate]):
    async def create_question(self, *, survey_id: int, obj_in: QuestionCreate, db: AsyncSession):
        db_question = Question(**obj_in.model_dump())
        db_question.survey_id = survey_id
        try:
            db.add(db_question)
            await db.commit()
            await db.refresh(db_question)
        except IntegrityError:
            await db.rollback()
        return db_question

    async def get_question(self, *, question_id: int, db: AsyncSession):
        question_in_db = await self.get(db=db, id=question_id)
        if not question_in_db:
            raise QuestionNotFoundException
        return question_in_db

    async def update_question(self, *, question_id: int, obj_in: QuestionUpdate, db: AsyncSession) -> Question:
        question_in_db = await self.get_question(db=db, question_id=question_id)
        return await self.update(obj_current=question_in_db, obj_in=obj_in, db=db)

    async def delete_question(self, *, question_id: int, db: AsyncSession):
        return await self.delete(db=db, id=question_id)


question = CRUDQuestion(Question)