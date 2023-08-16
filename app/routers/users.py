from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select


from ..auth import create_access_token, get_current_user, authenticate_user, Token,\
    ACCESS_TOKEN_EXPIRES_HOURS, get_password_hash
from ..database import get_session
from ..schemas import UserCreate, UserRead
from ..models import User
from ..crud import get_user_with_username, get_user_with_email


router = APIRouter(
    tags=['users'],
    prefix='/auth'
)


@router.post('/users', response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def register(session: Annotated[Session, Depends(get_session)],
                   data: Annotated[UserCreate, Body()]):
    if get_user_with_username(session=session, username=data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Duplicate username'
        )
    if get_user_with_email(session=session, email=data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Duplicate email'
        )
    hashed_password = get_password_hash(password=data.password)
    new_user = User(username=data.username,
                    email=data.email,
                    hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    user = authenticate_user(session=session,
                             username=data.username,
                             password=data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRES_HOURS)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
