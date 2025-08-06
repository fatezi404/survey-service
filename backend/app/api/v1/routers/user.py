from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user_model import User
from app.crud.user_crud import user
from app.schemas.user_schema import (
    UserLogin,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPasswordUpdate,
    UserDetails
)

router = APIRouter()


@router.post('/register', response_model=UserResponse, tags=['user'], status_code=status.HTTP_201_CREATED)
async def create_user(obj_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user_by_email = await user.get(db=db, email=obj_in.email)
    user_by_username = await user.get(db=db, username=obj_in.username)

    if user_by_username or user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this email or username already exists'
        )
    return await user.create_user(obj_in=obj_in, db=db)