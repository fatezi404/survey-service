from redis.asyncio import Redis
from datetime import timedelta

from app.models.user_model import User
from app.core.config import TokenType


async def add_token_to_redis(
    redis_client: Redis, user: User, token: str, token_type: TokenType, expires_delta: int | None = None
):
    token_key = f'user:{user.id}:{token_type}'

    await redis_client.sadd(token_key, token)
    if expires_delta:
        await redis_client.expire(token_key, timedelta(minutes=expires_delta))


async def get_valid_tokens(redis_client: Redis, user_id: int, token_type: TokenType):
    token_key = f'user:{user_id}:{token_type}'
    valid_token = await redis_client.smembers(token_key)
    return valid_token


async def delete_token(redis_client: Redis, user_id: int, token_type: TokenType):
    token_key = f'user:{user_id}:{token_type}'
    valid_token = await get_valid_tokens(redis_client, user_id, token_type)
    if valid_token is not None:
        await redis_client.delete(token_key)


async def update_token_in_redis(
    redis_client: Redis, user: User, token: str, token_type: TokenType, expires_delta: int | None = None
):
    await delete_token(redis_client, user.id, token_type)
    await add_token_to_redis(redis_client, user, token, token_type, expires_delta)
