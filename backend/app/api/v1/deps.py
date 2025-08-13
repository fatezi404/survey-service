from typing import Annotated

from jose import JWTError
from redis.asyncio import Redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose.exceptions import ExpiredSignatureError

from app.db.session import get_db, get_redis_db
from app.models.user_model import User
from app.crud.user_crud import user
from app.core.config import TokenType
from app.core.security import decode_token
from app.services.token import get_valid_tokens

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login/access-token')

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is expired',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    user_id = payload['sub']
    valid_token = await get_valid_tokens(redis_client, user_id, TokenType.ACCESS)
    if not valid_token or token not in valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    user_in_db: User = await user.get(db=db, id=int(user_id))
    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if not user_in_db.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is inactive')

    return user_in_db
