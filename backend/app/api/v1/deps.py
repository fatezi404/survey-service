from typing import Annotated
from jose import JWTError
from redis.asyncio import Redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from jose.exceptions import ExpiredSignatureError

from app.db.session import get_db, get_redis_db
from app.models.user_model import User
from app.models.role_model import Role
from app.core.config import TokenType
from app.core.security import decode_token
from app.services.token import get_valid_tokens
from app.services.permission import has_permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login/access-token')


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is expired', headers={'WWW-Authenticate': 'Bearer'}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect token', headers={'WWW-Authenticate': 'Bearer'}
        )
    user_id = payload['sub']
    valid_token = await get_valid_tokens(redis_client, user_id, TokenType.ACCESS)
    if not valid_token or token not in valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    result = await db.execute(
        select(User)
        .options(selectinload(User.direct_permissions), selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == int(user_id))
    )
    user_in_db = result.scalar_one_or_none()
    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if not user_in_db.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is inactive')

    return user_in_db


def require_permission(resource: str, action: str):
    async def permission_dependency(current_user: Annotated[User, Depends(get_current_user)]):
        context = {}
        if not await has_permission(current_user, resource, action, context):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f'Permission denied: {action} on {resource}'
            )
        return current_user

    return permission_dependency


def require_self_permission(resource: str, action: str):
    async def permission_dependency(user_id: int, current_user: Annotated[User, Depends(get_current_user)]):
        """Conditions = {'self': true}"""
        context = {'user_id': current_user.id, 'target_user_id': user_id}
        if not await has_permission(current_user, resource, action, context):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f'Permission denied: {action} on {resource}'
            )
        return current_user

    return permission_dependency
