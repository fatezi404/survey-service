from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserBase
from app.core.security import get_hashed_password
from app.utils.exceptions import NotFoundException

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def create_user(self, *, obj_in: UserCreate, db: AsyncSession) -> User:
        db_user = User(**obj_in.model_dump(exclude={'password'}))
        db_user.hashed_password = get_hashed_password(password=obj_in.password)
        try:
            db.add(db_user)
            await db.commit()
        except IntegrityError:
            await db.rollback()
        return db_user

    async def get_user(self, *, user_id: int,db: AsyncSession) -> User:
        user_obj = await self.get(db=db, id=user_id)
        if not user_obj:
            raise NotFoundException
        return user_obj

    async def get_user_by_email_or_username(self, *, identifier: str, db: AsyncSession) -> User | None:
        stmt = select(User).filter(or_(User.username == identifier, User.email == identifier))
        result = await db.execute(stmt)
        user_obj = result.scalar_one_or_none()
        return user_obj

    async def update_user(self, *, user_id: int, obj_in: UserUpdate, db: AsyncSession) -> User:
        user_obj = await self.get(db=db, id=user_id)
        if not user_obj:
            raise NotFoundException
        return await self.update(obj_current=user_obj, obj_in=obj_in, db=db)

    async def delete_user(self, *, user_id: int, db: AsyncSession):
        user_obj = await self.get(db=db, id=user_id)
        if not user_obj:
            raise NotFoundException
        return await self.delete(db=db, id=user_id)

user = CRUDUser(User)