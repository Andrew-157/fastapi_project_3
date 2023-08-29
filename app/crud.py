from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from .models import User, Tag, Question


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
