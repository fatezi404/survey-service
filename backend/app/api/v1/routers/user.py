from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user_model import User
from app.crud.user_crud import user
from app.schemas.user_schema import UserResponse, UserCreate, UserUpdate, UserDetails
from app.utils.exceptions import UserNotFoundException, NotFoundException
from app.api.v1.deps import require_self_permission, require_permission, get_current_user

router = APIRouter()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(obj_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """Create a user with email or username and a password.\n
    Password must be at least 8 characters long, must contain at least one digit,
    and at least one uppercase and lowercase letter."""

    user_by_email = await user.get(db=db, email=obj_in.email)
    user_by_username = await user.get(db=db, username=obj_in.username)

    if user_by_username or user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='User with this email or username already exists'
        )
    return await user.create_user(obj_in=obj_in, db=db)


@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        user_in_db = await user.get_user(db=db, user_id=current_user.id)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_in_db


@router.get('/', response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('user', 'list'))],
    skip: int = 0,
    limit: int = 100
):
    return await user.get_users(db=db, skip=skip, limit=limit)


@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_self_permission('user', 'read'))]
):
    try:
        user_in_db = await user.get_user(db=db, user_id=user_id)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_in_db


@router.get('/{user_id}/details', response_model=UserDetails, status_code=status.HTTP_200_OK)
async def get_user_detailed(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_self_permission('user', 'details'))]
):
    """Get detailed user information with assigned roles and direct permissions."""
    try:
        user_in_db = await user.get_user_detailed(db=db, user_id=user_id)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_in_db


@router.get('/identifier/{identifier}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_email_or_username(
    identifier: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('user', 'details'))],
):
    try:
        user_by_email_or_username = await user.get_user_by_email_or_username(db=db, identifier=identifier)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_by_email_or_username


@router.put('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    obj_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_self_permission('user', 'update'))]
):
    try:
        user_update = await user.update_user(db=db, user_id=user_id, obj_in=obj_in)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_update


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_self_permission('user', 'delete'))]
):
    if user_id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin is undeletable')
    try:
        user_delete = await user.delete_user(db=db, user_id=user_id)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_delete