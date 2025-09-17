from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.response_crud import response
from app.models.user_model import User
from app.schemas.response_schema import ResponseResponse, ResponseCreate
from app.utils.exceptions import ResponseNotFoundException
from app.api.v1.deps import get_current_user

router = APIRouter()


@router.post('/', response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
async def create_response(
    obj_in: ResponseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        response_create = await response.create_response(db=db, obj_in=obj_in)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Response already exists')
    return response_create


@router.get('/{response_id}', response_model=ResponseResponse, status_code=status.HTTP_200_OK)
async def get_response(
    response_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        response_in_db = await response.get_response(db=db, response_id=response_id)
    except ResponseNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Response not found')
    return response_in_db
