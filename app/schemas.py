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


class TagBase(SQLModel):
    name: str = Field(max_length=255, min_length=2)


class TagRead(TagBase):
    id: int


class QuestionBase(SQLModel):
    title: str = Field(max_length=255, min_length=5)
    content: str | None = Field(default=None, min_length=10)


class QuestionCreate(QuestionBase):
    # if tags are not set, [] is used
    tags: list[str] = Field(default=[])


class QuestionRead(QuestionBase):
    id: int
    published: datetime
    updated: datetime | None
    user: UserRead
    tags: list[TagRead]


class QuestionUpdate(SQLModel):
    title: str | None = Field(min_length=5, max_length=255, default=None)
    content: str | None = Field(default=None)
    tags: list[str] = Field(default=[])
