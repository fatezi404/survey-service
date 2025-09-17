from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.option_model import Option
from app.schemas.option_schema import OptionCreate, OptionUpdate
from app.utils.exceptions import OptionNotFoundException


class CRUDOption(CRUDBase[Option, OptionCreate, OptionUpdate]):
    async def create_option_bulk(self, *, obj_in: list[OptionCreate], db: AsyncSession):
        db_options = [Option(**opt.model_dump()) for opt in obj_in]
        try:
            db.add_all(db_options)
            await db.commit()
            for option_obj in db_options:
                await db.refresh(option_obj)
        except IntegrityError:
            await db.rollback()
        return db_options

    async def get_option(self, *, option_id: int, db: AsyncSession):
        option_in_db = await self.get(db=db, id=option_id)
        if not option_in_db:
            raise OptionNotFoundException
        return option_in_db

    async def update_option(self, *, option_id: int, obj_in: OptionUpdate, db: AsyncSession) -> Option:
        option_in_db = await self.get_option(db=db, option_id=option_id)
        return await self.update(obj_current=option_in_db, obj_in=obj_in, db=db)

    async def delete_option(self, *, option_id: int, db: AsyncSession):
        return await self.delete(db=db, id=option_id)


option = CRUDOption(Option)