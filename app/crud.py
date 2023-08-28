from sqlmodel import Session, select

from .models import User, Tag


def get_user_with_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def get_user_with_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def get_tag_by_name(session: Session, name: str) -> Tag | None:
    return session.exec(select(Tag).where(Tag.name == name)).first()
