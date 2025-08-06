import bcrypt

from jose import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import settings, ALGORITHM, TokenType

def get_hashed_password(password: str | bytes) -> str:
    if isinstance(password, str):
        password = password.encode()
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode()

def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(plain_password, hashed_password)

def create_access_token(subject: int, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'sub': str(subject),
        'jti': str(uuid4()),
        'exp': expire,
        'iat': datetime.now(),
        'type': TokenType.ACCESS
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: int, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'sub': str(subject),
        'jti': str(uuid4()),
        'exp': expire,
        'iat': datetime.now(),
        'type': TokenType.REFRESH
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, ALGORITHM)

#async def blacklist_token(token: str):
#    try:
#        payload = decode_token(token)
#        jti = payload.get('jti')
#        exp = payload.get('exp')
#        ttl = exp - int(datetime.now().timestamp())
#        if jti:
#            await
#