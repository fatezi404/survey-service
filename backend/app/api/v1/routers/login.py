from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.schemas.token_schema import TokenResponse
from app.db.session import get_db, get_redis_db
from app.models.user_model import User
from app.crud.user_crud import user
from app.schemas.user_schema import UserLogin
from app.services.auth import authenticate_user
from app.utils.exceptions import NotFoundException, WrongPasswordException
from app.core.config import settings

router = APIRouter()


@router.post('/access-token', response_model=TokenResponse, tags=['login'])
async def login_access_token(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
    oauth_form: OAuth2PasswordRequestForm = Depends()
):
    login_data = UserLogin(identifier=oauth_form.username, password=oauth_form.password)
    try:
        user_auth = await authenticate_user(db=db, data=login_data)
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found'
        )
    except WrongPasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Wrong email/username or password'
        )
    if not user_auth.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is inactive'
        )
    access_token = create_access_token(
        subject=user_auth.id, # fixme: wtf?
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = create_refresh_token(
        subject=user_auth.id, # fixme: wtf?
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
