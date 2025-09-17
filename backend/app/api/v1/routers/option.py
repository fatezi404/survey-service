from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.option_crud import option
from app.crud.survey_crud import survey
from app.crud.question_crud import question
from app.models.user_model import User
from app.schemas.option_schema import OptionResponse, OptionUpdate, OptionCreateBulk
from app.api.v1.deps import get_current_user, has_permission
from app.utils.exceptions import OptionNotFoundException, NotFoundException

router = APIRouter()


@router.post('/bulk', response_model=list[OptionResponse], status_code=status.HTTP_201_CREATED)
async def create_option_bulk(
    question_id: int,
    obj_in: OptionCreateBulk,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        question_in_db = await question.get_question(db=db, question_id=question_id)
        survey_in_db = await survey.get_survey(db=db, survey_id=question_in_db.survey_id)
        if not await has_permission(
            current_user, 'option', 'create', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: create on option')
        option_create_bulk = await option.create_option_bulk(db=db, question_id=question_id, obj_in=obj_in.options)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Option already exists')
    return option_create_bulk


@router.get('/{option_id}', response_model=OptionResponse, status_code=status.HTTP_200_OK)
async def get_option(
    option_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        option_in_db = await option.get_option(db=db, option_id=option_id)
        question_in_db = await question.get_question(db=db, question_id=option_in_db.question_id)
        survey_in_db = await survey.get_survey(db=db, survey_id=question_in_db.survey_id)
        if not await has_permission(
            current_user, 'option', 'read', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: read on option')
    except OptionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Option not found')
    return option_in_db


@router.put('/{option_id}', response_model=OptionResponse, status_code=status.HTTP_200_OK)
async def update_option(
    option_id: int,
    obj_in: OptionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        option_in_db = await option.get_option(db=db, option_id=option_id)
        question_in_db = await question.get_question(db=db, question_id=option_in_db.question_id)
        survey_in_db = await survey.get_survey(db=db, survey_id=question_in_db.survey_id)
        if not await has_permission(
            current_user, 'option', 'update', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: update on option')
        option_update = await option.update_option(db=db, option_id=option_id, obj_in=obj_in)
    except OptionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Option not found')
    return option_update


@router.delete('/{option_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_option(
    option_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        option_in_db = await option.get_option(db=db, option_id=option_id)
        question_in_db = await question.get_question(db=db, question_id=option_in_db.question_id)
        survey_in_db = await survey.get_survey(db=db, survey_id=question_in_db.survey_id)
        if not await has_permission(
            current_user, 'option', 'delete', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: delete on option')
        option_delete = await option.delete_option(db=db, option_id=option_id)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Option not found')
    return option_delete
