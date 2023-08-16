import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session, select


from app.models import User
from app.auth import generate_password_hash


from .conftest import AuthActions


def test_register(client: TestClient, session: Session):
    response = client.post(
        '/users', json={'username': 'user1',
                        'email': 'user1@gmail.com',
                        'password': '34somepassword34'}
    )

    assert response.status_code == status.HTTP_201_CREATED
    created_user = session.exec(
        select(User).where(User.username == 'user1')).first()
    assert created_user is not None
    expected_data = {
        'username': created_user.username,
        'email': created_user.email,
        'id': created_user.id
    }
    assert response.json() == expected_data


def test_register_with_empty_body(client: TestClient):
    response = client.post('/users', json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_with_no_body(client: TestClient):
    response = client.post('/users', json=None)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    ('username', 'email', 'password'),
    (
        ('new_', 'new_user@gmail.com', '34somepassword34'),
        (None, 'new_user@gmail.com', '34somepassword34'),
        ('new_user', 'not_valid_email', '34somepassword34'),
        ('new_user', None, '34somepassword34'),
        ('new_user', 'new_user@gmail.com', 'short'),
        ('new_user', 'new_user@gmail.com', None)
    )
)
def test_register_with_invalid_values(client: TestClient, username, email, password):
    response = client.post('/users', json={'username': username,
                                           'email': email,
                                           'password': password})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    ('username', 'email', 'password', 'detail'),
    (
        ('test_user', 'new_user@gmail.com',
         '34somepassword34', 'Duplicate username'),
        ('new_user', 'test_user@gmail.com', '34somepassword34', 'Duplicate email')
    )
)
def test_register_with_duplicate_values(client: TestClient, username, email, password, detail):
    response = client.post('/users', json={'username': username,
                                           'email': email,
                                           'password': password})
    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'detail' in response.json()
    assert response.json() == {'detail': detail}


def test_login_with_invalid_data(client: TestClient):
    response = client.post('/users/login', data={'username': 'no_one',
                                                 'password': 'nothing'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "www-authenticate" in dict(response.headers)
    assert dict(response.headers)["www-authenticate"] == "Bearer"
    assert 'detail' in response.json()
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_login(client: TestClient, session: Session):
    new_user = User(username='user1',
                    email='user1@gmail.com',
                    hashed_password=generate_password_hash('34somepassword34'))
    session.add(new_user)
    session.commit()
    response = client.post('/users/login', data={'username': new_user.username,
                                                 'password': '34somepassword34'})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_read_users_me(client: TestClient, auth: AuthActions, session: Session):
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/users/me', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    test_user = session.exec(select(User).where(
        User.username == 'test_user')).first()
    expected_data = {
        'username': test_user.username,
        'email': test_user.email,
        'id': test_user.id
    }
    assert response.json() == expected_data


def test_read_users_me_for_not_logged_user(client: TestClient):
    response = client.get('/users/me')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "www-authenticate" in dict(response.headers)
    assert dict(response.headers)["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    ('username', 'email'),
    (
        ('shor', None),
        (None, 'invalid'),
        ('shor', 'invalid')
    )
)
def test_update_user_validate_input(client: TestClient, auth: AuthActions, username, email):
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch('/users/me', json={'username': username,
                                               'email': email}, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_user_with_duplicate_username(client: TestClient, auth: AuthActions, session: Session):
    new_user = User(username='user1',
                    email='user1@gmail.com',
                    hashed_password=generate_password_hash('34somepassword34'))
    session.add(new_user)
    session.commit()
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch(
        '/users/me', json={'username': new_user.username}, headers=headers)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'detail' in response.json()
    assert response.json() == {'detail': 'Duplicate username'}


def test_update_user_with_duplicate_email(client: TestClient, auth: AuthActions, session: Session):
    new_user = User(username='user1',
                    email='user1@gmail.com',
                    hashed_password=generate_password_hash('34somepassword34'))
    session.add(new_user)
    session.commit()
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch(
        '/users/me', json={'email': new_user.email}, headers=headers)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'detail' in response.json()
    assert response.json() == {'detail': 'Duplicate email'}


def test_update_user_with_empty_body(client: TestClient, auth: AuthActions):
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch('/users/me', json={}, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.json()
    assert response.json() == {'detail': 'No data provided'}


def test_update_user_with_no_body(client: TestClient, auth: AuthActions):
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch('/users/me', json=None, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_user_username(client: TestClient, auth: AuthActions, session: Session):
    test_user = session.exec(select(User).where(
        User.username == 'test_user')).first()
    new_username = 'new_user'
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch('/users/me', json={'username': new_username},
                            headers=headers)
    assert response.status_code == status.HTTP_200_OK
    session.refresh(test_user)
    assert test_user.username == new_username
    expected_data = {
        'username': test_user.username,
        'email': test_user.email,
        'id': test_user.id
    }
    assert response.json() == expected_data


def test_update_user_email(client: TestClient, auth: AuthActions, session: Session):
    test_user = session.exec(select(User).where(
        User.username == 'test_user')).first()
    new_email = 'new_email@gmail.com'
    token = auth.login()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.patch('/users/me', json={'email': new_email},
                            headers=headers)
    assert response.status_code == status.HTTP_200_OK
    session.refresh(test_user)
    assert test_user.email == new_email
    expected_data = {
        'username': test_user.username,
        'email': test_user.email,
        'id': test_user.id
    }
    assert response.json() == expected_data


def test_update_user_for_not_logged_user(client: TestClient):
    response = client.patch('/users/me', json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "www-authenticate" in dict(response.headers)
    assert dict(response.headers)["www-authenticate"] == "Bearer"
