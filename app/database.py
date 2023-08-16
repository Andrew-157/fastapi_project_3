from sqlmodel import Session, create_engine
from decouple import config


DATABASE_URL = config("DATABASE_URL")


engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
