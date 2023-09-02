from sqlmodel import Session, select, and_
from sqlalchemy import asc, desc
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
                      offset: int | None = None,
                      search_string: str | None = None):
    if search_string:
        return session.exec(
            select(Question).where(Question.title.contains(search_string)).
            offset(offset=offset).
            limit(limit=limit).
            options(
                joinedload(Question.tags),
                joinedload(Question.user)
            ).order_by(asc(Question.id))).unique().all()
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


def get_all_answers(session: Session,
                    question_id: int,
                    offset: int | None = None,
                    limit: int | None = None,
                    by_date_asc: bool | None = None):
    ordering = None
    if by_date_asc == None:
        ordering = asc(Answer.id)
    if by_date_asc == True:
        ordering = asc(Answer.published)
    if by_date_asc == False:
        ordering = desc(Answer.published)
    return session.exec(
        select(Answer).
        where(Answer.question_id == question_id).
        offset(offset=offset).limit(limit=limit).
        options(joinedload(Answer.user)).
        order_by(ordering)).all()
