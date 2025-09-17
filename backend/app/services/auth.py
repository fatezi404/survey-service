from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.crud.user_crud import user
from app.utils.exceptions import WrongPasswordException, UserNotFoundException
from app.core.security import verify_password
from app.schemas.user_schema import UserLogin


async def authenticate_user(data: UserLogin, db: AsyncSession) -> User | None:
    user_obj = await user.get_user_by_email_or_username(identifier=data.identifier, db=db)
    if not user_obj:
        raise UserNotFoundException
    if not verify_password(plain_password=data.password, hashed_password=user_obj.hashed_password):
        raise WrongPasswordException
    return user_obj
