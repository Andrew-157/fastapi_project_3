from sqlmodel import Session, select, and_
from sqlalchemy import asc
from sqlalchemy.orm import joinedload

from .models import User, Tag, Question, Answer


def get_user_with_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def get_user_with_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def get_tag_by_name(session: Session, name: str) -> Tag | None:
    return session.exec(select(Tag).where(Tag.name == name)).first()


def get_question_by_id(session: Session, id: int) -> Question | None:
    return session.exec(select(Question).
                        where(Question.id == id).
                        options(joinedload(Question.tags), joinedload(Question.user))).first()


def get_all_questions(session: Session,
                      limit: int | None = None,
                      offset: int | None = None):
    return session.exec(
        select(Question).
        offset(offset=offset).
        limit(limit=limit).
        options(
            joinedload(Question.tags),
            joinedload(Question.user)
        ).order_by(asc(Question.id))).unique().all()


def get_answer_by_id_and_question_id(session: Session,
                                     question_id: int,
                                     id: int) -> Answer | None:
    return session.exec(
        select(Answer).
        where(and_(Answer.id == id,
                   Answer.question_id == question_id)).
        options(
            joinedload(Answer.user)
        )).first()
