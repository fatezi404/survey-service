from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.response_model import Response
from app.models.user_model import User
from app.schemas.response_schema import ResponseCreate, ResponseUpdate
from app.utils.exceptions import ResponseNotFoundException


class CRUDResponse(CRUDBase[Response, ResponseCreate, ResponseUpdate]):
    async def create_response(
        self,
        *,
        obj_in: ResponseCreate,
        db: AsyncSession,
        current_user: User
    ):
        db_response = Response(**obj_in.model_dump())
        try:
            db.add(db_response)
            await db.commit()
            await db.refresh(db_response)
        except IntegrityError:
            await db.rollback()
        return db_response

    async def get_response(self, *, response_id: int, db: AsyncSession):
        response_in_db = await self.get(db=db, id=response_id)
        if not response_in_db:
            raise ResponseNotFoundException
        return response_in_db


response = CRUDResponse(Response)
