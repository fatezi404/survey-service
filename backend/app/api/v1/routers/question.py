from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.question_crud import question
from app.crud.survey_crud import survey
from app.models.user_model import User
from app.schemas.question_schema import QuestionResponse, QuestionCreate, QuestionUpdate, QuestionDetails
from app.api.v1.deps import get_current_user, has_permission
from app.utils.exceptions import QuestionNotFoundException, NotFoundException, SurveyNotFoundException

router = APIRouter()


@router.post('/', response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    obj_in: QuestionCreate,
    survey_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
        if not await has_permission(
            current_user, 'question', 'create', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: create on question')
        question_create = await question.create_question(db=db, survey_id=survey_id, obj_in=obj_in)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Question already exists')
    except SurveyNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Survey not found')
    return question_create


@router.get('/{question_id}', response_model=QuestionResponse, status_code=status.HTTP_200_OK)
async def get_question(
    survey_id: int,
    question_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
        if not await has_permission(
            current_user, 'question', 'read', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: read on question')
        question_in_db = await question.get_question(db=db, question_id=question_id)
    except QuestionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question not found')
    return question_in_db


@router.get('/{question_id}/options', response_model=QuestionDetails, status_code=status.HTTP_200_OK)
async def get_question_options(
    survey_id: int,
    question_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
        if not await has_permission(
            current_user, 'question', 'details', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: details on question')
        question_in_db = await question.get_question(db=db, question_id=question_id)
    except QuestionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question not found')
    return question_in_db


@router.put('/{question_id}', response_model=QuestionResponse, status_code=status.HTTP_200_OK)
async def update_question(
    survey_id: int,
    question_id: int,
    obj_in: QuestionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
        if not await has_permission(
            current_user, 'question', 'update', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: update on question')
        question_update = await question.update_question(db=db, question_id=question_id, obj_in=obj_in)
    except QuestionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question not found')
    return question_update


@router.delete('/{question_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    survey_id: int,
    question_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
        if not await has_permission(
            current_user, 'question', 'delete', {'user_id': current_user.id, 'creator_id': survey_in_db.creator_id}
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied: delete on question')
        question_delete = await question.delete_question(db=db, question_id=question_id)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question not found')
    return question_delete
