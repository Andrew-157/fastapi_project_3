from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, BaseModel


class RootModel(BaseModel):
    is_root: bool = True


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True,
                          max_length=255, min_length=5)

    email: EmailStr = Field(unique=True, index=True)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    username: str | None = Field(max_length=255, min_length=5,
                                 default=None)
    email: EmailStr | None = Field(default=None)


class QuestionBase(SQLModel):
    title: str = Field(max_length=255, min_length=5)
    content: str


class QuestionCreate(QuestionBase):
    tags: list[str] = Field(min_items=1)


class QuestionRead(QuestionBase):
    id: int
    published: datetime
    updated: datetime | None
    user: UserRead
    tags: list["TagRead"]


class QuestionUpdate(SQLModel):
    title: str | None = Field(min_length=5, max_length=255)
    content: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)


class TagBase(SQLModel):
    name: str = Field(max_length=255, min_length=5)


class TagRead(TagBase):
    id: int
