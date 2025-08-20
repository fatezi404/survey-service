from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.role_model import Role
from app.crud.user_crud import user
from app.schemas.role_schema import RoleCreate, RoleUpdate
from utils.exceptions import RoleNotFoundException


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):  # todo: add permissions
    async def create_role(self, *, obj_in: RoleCreate, db: AsyncSession):
        db_role = Role(**obj_in.model_dump())
        try:
            db.add(db_role)
            await db.commit()
            await db.refresh(db_role)
        except IntegrityError:
            await db.rollback()
        return db_role

    async def get_role(self, *, role_id: int, db: AsyncSession) -> Role:
        role_in_db = await self.get(db=db, id=role_id)
        if not role_in_db:
            raise RoleNotFoundException
        return role_in_db

    async def get_roles(self, *, skip: int = 0, limit: int = 100, db: AsyncSession):
        stmt = select(Role).offset(skip).limit(limit)
        result = await db.execute(stmt)
        roles = result.scalars().all()
        return roles

    async def update_role(self, *, role_id: int, obj_in: RoleUpdate, db: AsyncSession):
        role_in_db = await self.get_role(db=db, role_id=role_id)
        return await self.update(obj_current=role_in_db, obj_in=obj_in, db=db)

    async def delete_role(self, *, role_id: int, db: AsyncSession):
        return await self.delete(db=db, id=role_id)

    async def assign_role_to_user(
        self, *, role_id: int, user_id: int, db: AsyncSession
    ):
        role_in_db = await self.get_role(db=db, role_id=role_id)
        user_in_db = await user.get_user(db=db, user_id=user_id)
        if role_in_db not in user_in_db.roles:
            user_in_db.roles.append(role_in_db)
            await db.commit()
            await db.refresh(user_in_db)
        return user_in_db

    async def remove_role_from_user(
        self, *, role_id: int, user_id: int, db: AsyncSession
    ):
        role_in_db = await self.get_role(db=db, role_id=role_id)
        user_in_db = await user.get_user(db=db, user_id=user_id)
        if role_in_db in user_in_db.roles:
            user_in_db.roles.remove(role_in_db)
            await db.commit()
            await db.refresh(user_in_db)
        return user_in_db


role = CRUDRole(Role)
