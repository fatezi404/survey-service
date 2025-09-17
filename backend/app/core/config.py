from enum import Enum
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

ALGORITHM = 'HS256'


class TokenType(str, Enum):
    ACCESS = 'access_token'
    REFRESH = 'refresh_token'


class QuestionType(str, Enum):
    SINGLE = 'single_choice'
    MULTIPLE = 'multiple_choice'
    TEXT = 'text'


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    REDIS_URL: RedisDsn
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 42069

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
