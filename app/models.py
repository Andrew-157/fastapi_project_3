from sqlmodel import Field

from .schemas import UserBase


class User(UserBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    hashed_password: str
