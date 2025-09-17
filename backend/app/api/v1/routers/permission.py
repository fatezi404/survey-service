from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.permission_crud import permission
from app.models.user_model import User
from app.schemas.permission_schema import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.role_schema import RoleDetails
from app.api.v1.deps import require_permission
from app.utils.exceptions import (
    PermissionNotFoundException,
    NotFoundException,
    RoleNotFoundException,
    PermissionAlreadyAssignedException,
    RoleHasNoThisPermissionException,
)

router = APIRouter()


@router.post('/', response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    obj_in: PermissionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'create'))],
):
    try:
        permission_create = await permission.create_permission(db=db, obj_in=obj_in)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Permission already exists')
    return permission_create


@router.get('/', response_model=list[PermissionResponse], status_code=status.HTTP_200_OK)
async def get_permissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'list'))],
    skip: int = 0,
    limit: int = 100,
):
    return await permission.get_permissions(db=db, skip=skip, limit=limit)


@router.get('/{permission_id}', response_model=PermissionResponse, status_code=status.HTTP_200_OK)
async def get_permission(
    permission_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'read'))],
):
    try:
        permission_in_db = await permission.get_permission(db=db, permission_id=permission_id)
    except PermissionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found')
    return permission_in_db


@router.put('/{permission_id}', response_model=PermissionResponse, status_code=status.HTTP_200_OK)
async def update_permission(
    permission_id: int,
    obj_in: PermissionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'update'))],
):
    try:
        permission_update = await permission.update_permission(db=db, permission_id=permission_id, obj_in=obj_in)
    except PermissionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found')
    return permission_update


@router.delete('/{permission_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'delete'))],
):
    try:
        permission_delete = await permission.delete_permission(db=db, permission_id=permission_id)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found')
    return permission_delete


@router.post('/{permission_id}/assign/{role_id}', response_model=RoleDetails, status_code=status.HTTP_200_OK)
async def assign_permission_to_role(
    permission_id: int,
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'assign'))],
):
    try:
        permission_assignment = await permission.assign_permission_to_role(
            db=db, permission_id=permission_id, role_id=role_id
        )
    except PermissionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found')
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    except PermissionAlreadyAssignedException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Permission already assigned to this role')
    return permission_assignment


@router.delete('/{permission_id}/remove/{role_id}', response_model=RoleDetails, status_code=status.HTTP_200_OK)
async def remove_permission_from_role(
    permission_id: int,
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('permission', 'remove'))],
):
    try:
        permission_remove = await permission.remove_permission_from_role(
            db=db, permission_id=permission_id, role_id=role_id
        )
    except PermissionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found')
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    except RoleHasNoThisPermissionException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role does not have this permission')
    return permission_remove
