from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta


from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    get_hashed_password,
)
from app.schemas.token_schema import TokenResponse, TokenResponseWithType
from app.schemas.user_schema import UserPasswordUpdate
from app.db.session import get_db, get_redis_db
from app.models.user_model import User
from app.crud.user_crud import user
from app.schemas.user_schema import UserLogin
from app.services.auth import authenticate_user
from app.services.token import get_valid_tokens, update_token_in_redis
from app.utils.exceptions import WrongPasswordException, UserNotFoundException
from app.core.config import settings, TokenType
from app.api.v1.deps import get_current_user

router = APIRouter()


@router.post("/access-token", response_model=TokenResponseWithType)
async def login_access_token(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
    oauth_form: OAuth2PasswordRequestForm = Depends(),
):
    login_data = UserLogin(identifier=oauth_form.username, password=oauth_form.password)
    try:
        user_auth = await authenticate_user(db=db, data=login_data)
    except UserNotFoundException:
        if "@" in oauth_form.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The e-mail address and/or password you specified are not correct",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The username and/or password you specified are not correct",
            )
    except WrongPasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong email/username or password",
        )
    if not user_auth.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive"
        )
    access_token = create_access_token(
        subject=user_auth.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=user_auth.id,
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    await update_token_in_redis(
        redis_client=redis_client,
        user=user,
        token=access_token,
        token_type=TokenType.ACCESS,
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await update_token_in_redis(
        redis_client=redis_client,
        user=user,
        token=refresh_token,
        token_type=TokenType.REFRESH,
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return TokenResponseWithType(access_token=access_token, token_type="bearer")


@router.post("/new-access-token", response_model=TokenResponseWithType)
async def create_new_access_token(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: TokenResponse = Body(),
):
    try:
        payload = decode_token(body.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is expired"
        )
    if payload["type"] == "refresh":
        user_id = payload["sub"]
        valid_refresh_token = await get_valid_tokens(
            redis_client=redis_client, user_id=user_id, token_type=TokenType.REFRESH
        )
        if not valid_refresh_token or body.refresh_token not in valid_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong credentials or invalid refresh token",
            )
        user_in_db: User = await user.get(db=db, id=int(user_id))
        if user_in_db.is_active:
            access_token = create_access_token(
                user_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            await update_token_in_redis(
                redis_client=redis_client,
                user=user_in_db,
                token=access_token,
                token_type=TokenType.ACCESS,
                expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect token"
        )
    return TokenResponseWithType(access_token=access_token, token_type="bearer")


@router.post("/change-password")
async def change_password(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
    password_payload: UserPasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not verify_password(
        password_payload.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is wrong"
        )

    new_password_hashed = get_hashed_password(password_payload.new_password)
    await user.update_user(
        user_id=current_user.id, obj_in={"hashed_password": new_password_hashed}, db=db
    )

    access_token = create_access_token(
        current_user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        current_user.id, timedelta(minutes=settings.REFREsH_TOKEN_EXPIRE_MINUTES)
    )

    await update_token_in_redis(
        redis_client,
        current_user,
        access_token,
        TokenType.ACCESS,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await update_token_in_redis(
        redis_client,
        current_user,
        refresh_token,
        TokenType.REFRESH,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password has been changed successfully"},
    )
