from sqlmodel import Session, select

from .models import User


def get_user_with_username(session: Session, username: str) -> User:
    return session.exec(select(User).where(User.username == username)).first()
