from sqlmodel import SQLModel, Field
from pydantic import EmailStr, BaseModel


class RootModel(BaseModel):
    is_root: bool = True


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True,
                          max_length=255, min_length=5)

    email: EmailStr = Field(unique=True, index=True)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UpdateUser(SQLModel):
    username: str | None = Field(max_length=255, min_length=5,
                                 default=None)
    email: EmailStr | None = Field(default=None)
