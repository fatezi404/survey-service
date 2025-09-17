from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.role_crud import role
from app.models.user_model import User
from app.schemas.role_schema import RoleResponse, RoleDetails, RoleCreate, RoleUpdate
from app.schemas.user_schema import UserDetails
from app.api.v1.deps import require_permission
from app.utils.exceptions import (
    RoleNotFoundException,
    NotFoundException,
    UserNotFoundException,
    RoleAlreadyAssignedException,
    UserHasNoThisRoleException,
)

router = APIRouter()


@router.post('/', response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    obj_in: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'create'))],
):
    try:
        role_create = await role.create_role(db=db, obj_in=obj_in)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Permission already exists')
    return role_create


@router.get('/{role_id}', response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def get_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'read'))],
):
    try:
        role_in_db = await role.get_role(db=db, role_id=role_id)
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    return role_in_db


@router.get('/', response_model=list[RoleResponse], status_code=status.HTTP_200_OK)
async def get_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'list'))],
    skip: int = 0,
    limit: int = 100,
):
    return await role.get_roles(db=db, skip=skip, limit=limit)


@router.get('/{role_id}/details', response_model=RoleDetails, status_code=status.HTTP_200_OK)
async def get_role_detailed(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'details'))],
):
    try:
        role_in_db = await role.get_role(db=db, role_id=role_id)
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    return role_in_db


@router.put('/{role_id}', response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def update_role(
    role_id: int,
    obj_in: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'update'))],
):
    try:
        role_update = await role.update_role(db=db, role_id=role_id, obj_in=obj_in)
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    return role_update


@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'delete'))],
):
    try:
        role_delete = await role.delete_role(db=db, role_id=role_id)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    return role_delete


@router.post('/{role_id}/assign/{user_id}', response_model=UserDetails, status_code=status.HTTP_200_OK)
async def assign_role_to_user(
    role_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'assign'))],
):
    try:
        role_assignment = await role.assign_role_to_user(db=db, role_id=role_id, user_id=user_id)
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    except RoleAlreadyAssignedException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role already assigned to this user')
    return role_assignment


@router.delete('/{role_id}/remove/{user_id}', response_model=UserDetails, status_code=status.HTTP_200_OK)
async def remove_role_from_user(
    role_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('role', 'remove'))],
):
    try:
        role_remove = await role.remove_role_from_user(db=db, role_id=role_id, user_id=user_id)
    except RoleNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    except UserHasNoThisRoleException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User does not have this role')
    return role_remove
