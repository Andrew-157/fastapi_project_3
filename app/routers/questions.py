from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlmodel import Session


from ..auth import get_current_user
from ..database import get_session
from ..crud import get_tag_by_name
from ..schemas import QuestionCreate, QuestionRead, QuestionUpdate
from ..models import Question, Tag, User


router = APIRouter(
    tags=['questions']
)


def get_tags_objects(tags: list[str], session: Session) -> list[Tag]:
    tags_objects_list = []
    for tag in tags:
        tag: str = tag.strip().replace(' ', '-')
        tag_object = get_tag_by_name(session=session, name=tag)
        if tag_object:
            tags_objects_list.append(tag_object)
        else:
            new_tag_object = Tag(name=tag)
            print(new_tag_object)
            tags_objects_list.append(new_tag_object)

    return tags_objects_list


@router.post('/questions',
             response_model=QuestionRead,
             status_code=status.HTTP_201_CREATED)
async def post_question(user: Annotated[User, Depends(get_current_user)],
                        data: Annotated[QuestionCreate, Body()],
                        session: Annotated[Session, Depends(get_session)]):
    tags = get_tags_objects(tags=data.tags, session=session)
    print(tags)
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
