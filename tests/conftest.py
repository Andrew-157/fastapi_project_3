import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import User
from app.auth import generate_password_hash

DATABASE_TEST_URL = 'sqlite:///:memory:'


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine(url=DATABASE_TEST_URL,
                           connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        test_user = User(username='test_user',
                         email='test_user@gmail.com',
                         hashed_password=generate_password_hash('34qwerty34'))
        session.add(test_user)
        session.commit()
        yield session


@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.debug = False
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class AuthActions(object):

    def __init__(self, client: TestClient):
        self._client = client

    def login(self,
              username: str | None = 'test_user',
              password: str | None = '34qwerty34'):
        response = self._client.post(
            '/users/login', data={'username': username,
                                  'password': password}
        )
        token = response.json()["access_token"]
        return token


@pytest.fixture
def auth(client: TestClient):
    return AuthActions(client)
