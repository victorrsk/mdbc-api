from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from pwdlib import PasswordHash
from sqlmodel import Session, select

from src.database.engine import get_engine
from src.models.users import User
from src.schemas.schemas import UserIn, UserOut

router = APIRouter(prefix='/users', tags=['users'])


pwd_context = PasswordHash.recommended()


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn):
    # FIXME: create sanitization function
    user.username = user.username.lower().replace(' ', '')
    user.email = user.email.replace(' ', '')
    user.password = pwd_context.hash(user.password.replace(' ', ''))

    user_db = User(
        id=None, username=user.username, email=user.email, password=user.password
    )

    with Session(get_engine()) as session:
        result = session.scalar(
            select(User).where(
                (User.username == user_db.username) | (User.email == user_db.email)
            )
        )
        if result:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='username or email already in use',
            )
        session.add(user_db)
        session.commit()
        session.refresh(user_db)

    return user_db


# FIXME improve read_user


@router.get('/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
def read_user(user_id: Annotated[int, Path(gt=0)]):
    with Session(get_engine()) as session:
        user_db = session.scalar(select(User).where(User.id == user_id))
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='user id not found'
            )
        return user_db
