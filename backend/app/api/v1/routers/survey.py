from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.survey_crud import survey
from app.models.user_model import User
from app.schemas.survey_schema import (
    SurveyUpdate,
    SurveyCreate,
    SurveyDetails,
    SurveyResponse,
    SurveyDetailsWithResponses,
)
from app.utils.exceptions import SurveyNotFoundException, NotFoundException
from app.api.v1.deps import require_permission, get_current_user

router = APIRouter()


@router.post('/', response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    obj_in: SurveyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('survey', 'create'))],
):
    """Create a survey with a title (amount for characters is min. 3 and max. 64) and description."""
    try:
        survey_create = await survey.create_survey(db=db, obj_in=obj_in, current_user=current_user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Survey already exists')
    return survey_create


@router.get('/', response_model=list[SurveyResponse], status_code=status.HTTP_200_OK)
async def get_surveys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('survey', 'list'))],
    skip: int = 0,
    limit: int = 100,
):
    return await survey.get_surveys(db=db, skip=skip, limit=limit)


@router.get('/list/', response_model=list[SurveyResponse], status_code=status.HTTP_200_OK)  # todo: test
async def get_user_surveys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
):
    return await survey.get_user_surveys(skip=skip, limit=limit, db=db, current_user=current_user)


@router.get('/{survey_id}', response_model=SurveyResponse, status_code=status.HTTP_200_OK)
async def get_survey(survey_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
    except SurveyNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Survey not found')
    return survey_in_db


@router.get('/{survey_id}/questions', response_model=SurveyDetails, status_code=status.HTTP_200_OK)
async def get_survey_questions(
    survey_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('survey', 'details'))],
):
    try:
        survey_in_db = await survey.get_survey(db=db, survey_id=survey_id)
    except SurveyNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Survey not found')
    return survey_in_db


@router.get('/{survey_id}/responses', response_model=SurveyDetailsWithResponses, status_code=status.HTTP_200_OK)
async def get_survey_with_responses(
    survey_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('survey', 'details'))],
):
    try:
        survey_with_responses = await survey.get_survey_with_responses(db=db, survey_id=survey_id)
    except SurveyNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Survey not found')
    return survey_with_responses


@router.put('/{survey_id}', response_model=SurveyResponse, status_code=status.HTTP_200_OK)
async def update_survey(
    survey_id: int,
    obj_in: SurveyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('survey', 'update'))],
):
    try:
        survey_update = await survey.update_survey(db=db, survey_id=survey_id, obj_in=obj_in)
    except SurveyNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Survey not found')
    return survey_update


@router.delete('/{survey_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(
    survey_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission('survey', 'delete'))],
):
    try:
        survey_delete = await survey.delete_survey(db=db, survey_id=survey_id)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Survey not found')
    return survey_delete
