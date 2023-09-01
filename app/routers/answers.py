from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from sqlmodel import Session


from ..auth import get_current_user
from ..database import get_session
from ..schemas import AnswerRead, AnswerCreateUpdate
from ..models import Answer, User, Question

router = APIRouter(
    tags=['answers']
)


@router.post('/questions/{question_id}/answers', response_model=AnswerRead)
async def post_answer(
    user: Annotated[User, Depends(get_current_user)],
    question_id: Annotated[int, Path(gt=1)],
    data: Annotated[AnswerCreateUpdate, Body()],
    session: Annotated[Session, Depends(get_session)]
):
    question = session.get(Question, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'QUestion with id {question_id} was not found.'
        )
    answer = Answer(
        content=data.content,
        question=question,
        user=user
    )
    session.add(answer)
    session.commit()
    session.refresh(answer)
    return answer
