from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.permission_model import Permission
from app.crud.role_crud import role
from app.schemas.permission_schema import PermissionCreate, PermissionUpdate
from utils.exceptions import (
    PermissionNotFoundException,
    PermissionAlreadyAssignedException,
    RoleHasNoThisPermissionException,
)


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    async def create_permission(self, *, obj_in: PermissionCreate, db: AsyncSession):
        db_permission = Permission(**obj_in.model_dump())
        try:
            db.add(db_permission)
            await db.commit()
            await db.refresh(db_permission)
        except IntegrityError:
            await db.rollback()
        return db_permission

    async def get_permission(self, *, permission_id: int, db: AsyncSession) -> Permission:
        permission_in_db = await self.get(db=db, id=permission_id)
        if not permission_in_db:
            raise PermissionNotFoundException
        return permission_in_db

    async def get_permissions(self, *, skip: int = 0, limit: int = 100, db: AsyncSession):
        stmt = select(Permission).offset(skip).limit(limit)
        result = await db.execute(stmt)
        permissions = result.scalars().all()
        return permissions

    async def update_permission(self, *, permission_id: int, obj_in: PermissionUpdate, db: AsyncSession):
        permission_in_db = await self.get_permission(db=db, permission_id=permission_id)
        return await self.update(obj_current=permission_in_db, obj_in=obj_in, db=db)

    async def delete_permission(self, *, permission_id: int, db: AsyncSession):
        return await self.delete(db=db, id=permission_id)

    async def assign_permission_to_role(self, *, permission_id: int, role_id: int, db: AsyncSession):
        permission_in_db = await self.get_permission(db=db, permission_id=permission_id)
        role_in_db = await role.get_role(db=db, role_id=role_id)

        if permission_in_db not in role_in_db.permissions:
            role_in_db.roles.append(permission_in_db)
            await db.commit()
            await db.refresh(role_in_db)
        else:
            raise PermissionAlreadyAssignedException

        return role_in_db

    async def remove_permission_from_role(self, *, permission_id: int, role_id: int, db: AsyncSession):
        permission_in_db = await self.get_permission(db=db, permission_id=permission_id)
        role_in_db = await role.get_role(db=db, role_id=role_id)
        if permission_in_db in role_in_db.permissions:
            role_in_db.permissions.remove(permission_in_db)
            await db.commit()
            await db.refresh(role_in_db)
        else:
            raise RoleHasNoThisPermissionException

        return role_in_db


permission = CRUDPermission(Permission)
