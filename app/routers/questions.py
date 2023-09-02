from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status, Path, Query
from sqlmodel import Session


from ..auth import get_current_user
from ..database import get_session
from ..crud import get_tag_by_name, get_question_by_id, get_all_questions
from ..schemas import QuestionCreate, QuestionRead, QuestionUpdate
from ..models import Question, Tag, User


router = APIRouter(
    tags=['questions']
)


def get_tags_objects(tags: list[str], session: Session) -> list[Tag]:
    tags_objects_list = []
    for tag in tags:
        tag: str = tag.strip().replace(' ', '-').lower()
        tag_object = get_tag_by_name(session=session, name=tag)
        if tag_object:
            tags_objects_list.append(tag_object)
        else:
            new_tag_object = Tag(name=tag)
            tags_objects_list.append(new_tag_object)

    return tags_objects_list


@router.get('/questions', response_model=list[QuestionRead])
async def get_questions(*,
                        session: Annotated[Session, Depends(get_session)],
                        offset: Annotated[int | None, Query(gt=0)] = None,
                        limit: Annotated[int | None, Query(gt=0)] = None,
                        search_string: Annotated[str | None, Query()] = None):
    questions = get_all_questions(
        session=session, offset=offset, limit=limit, search_string=search_string)
    return questions


@router.post('/questions',
             response_model=QuestionRead,
             status_code=status.HTTP_201_CREATED)
async def post_question(user: Annotated[User, Depends(get_current_user)],
                        data: Annotated[QuestionCreate, Body()],
                        session: Annotated[Session, Depends(get_session)]):
    # if tags are not set, [] will be used as it is defined as default value
    tags = get_tags_objects(tags=data.tags, session=session)
    question = Question(
        title=data.title,
        content=data.content,
        tags=tags,
        user=user
    )
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@router.get('/questions/{id}', response_model=QuestionRead)
async def get_question(id: Annotated[int, Path()],
                       session: Annotated[Session, Depends(get_session)]):
    question = get_question_by_id(session=session, id=id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Question with id {id} was not found.'
        )
    return question


@router.patch('/questions/{id}', response_model=QuestionRead)
async def update_question(id: Annotated[int, Path()],
                          session: Annotated[Session, Depends(get_session)],
                          data: Annotated[QuestionUpdate, Body()],
                          user: Annotated[User, Depends(get_current_user)]):
    question = session.get(Question, id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Question with id {id} was not found.'
        )
    if question.user != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Current user has no permission to update question with id {id}.'
        )
    data: dict = data.dict(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No data was provided for update.'
        )
    new_title = data.get('title')
    if new_title:
        question.title = new_title
    # both content and tags are done this way
    # so that by explicitly setting content to None and tags to []
    # content is removed and tags are also removed
    if 'content' in data:
        question.content = data['content']
    if 'tags' in data:
        tags_objects_list = get_tags_objects(
            session=session, tags=data['tags'])
        question.tags = tags_objects_list
    question.updated = datetime.utcnow()
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@router.delete('/questions/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(id: Annotated[int, Path()],
                          session: Annotated[Session, Depends(get_session)],
                          user: Annotated[User, Depends(get_current_user)]):
    question = session.get(Question, id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Question with id {id} was not found.'
        )
    if question.user != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Current user has no permission to delete question with id {id}.'
        )
    session.delete(question)
    session.commit()
    return None
