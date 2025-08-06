from typing import Annotated
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login/access-token')
