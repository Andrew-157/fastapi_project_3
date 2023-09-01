from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from .schemas import UserBase, QuestionBase, TagBase, AnswerBase


class User(UserBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    hashed_password: str

    questions: list["Question"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "delete"})
    answers: list["Answer"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "delete"})


class TaggedQuestions(SQLModel, table=True):
    __tablename__ = 'tagged_questions'
    question_id: int | None = Field(
        foreign_key='question.id', primary_key=True, default=None
    )
    tag_id: int | None = Field(
        foreign_key='tag.id', primary_key=True, default=None
    )


class Question(QuestionBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    published: datetime = Field(default=datetime.utcnow())
    updated: datetime | None = Field(default=None)
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates='questions')
    tags: list["Tag"] = Relationship(link_model=TaggedQuestions)
    answers: list["Answer"] = Relationship(back_populates='question',
                                           sa_relationship_kwargs={"cascade": "delete"})


class Tag(TagBase, table=True):
    id: int | None = Field(primary_key=True, default=None)


class Answer(AnswerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    question_id: int = Field(foreign_key="question.id")
    published: datetime = Field(default=datetime.utcnow())
    updated: datetime | None = Field(default=None)

    user: User = Relationship(back_populates="answers")
    question: Question = Relationship(back_populates="answers")
