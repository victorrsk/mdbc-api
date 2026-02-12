from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session, select

from src.database.session import get_session
from src.database.utils import clean_user_data
from src.models.users import User
from src.schemas.schemas import UserIn, UserList, UserOut
from src.security import get_pwd_hash

router = APIRouter(prefix='/users', tags=['users'])

# types
T_Session = Annotated[Session, Depends(get_session)]
T_PositiveInt = Annotated[int, Path(gt=0)]


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn, session: T_Session):
    user = clean_user_data(user)
    user.password = get_pwd_hash(user.password)
    user_db = User(
        id=None, username=user.username, email=user.email, password=user.password
    )

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


@router.get('/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
def read_user(user_id: T_PositiveInt, session: T_Session):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='user not found'
        )
    return user_db


@router.get('/', response_model=UserList)
def read_users(session: T_Session):
    users_list = session.scalars(select(User))

    return {'users': users_list}


# FIXME
# erro de unique constraint


@router.put('/{user_id}', response_model=UserOut)
def update_user(user_id: T_PositiveInt, user: UserIn, session: T_Session):
    user = clean_user_data(user)
    user.password = get_pwd_hash(user.password)

    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='user not found'
        )
    test_user = session.scalar(
        select(User).where(
            ((User.username == user_db.username) | (User.email == user_db.email))
            & (User.id != user_id)
        )
    )
    if test_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='username or email already in use',
        )
    user_db.username = user.username
    user_db.email = user.email
    user_db.password = user.password

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
def delete_user(user_id: T_PositiveInt, session: T_Session):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            detail='user not found', status_code=status.HTTP_404_NOT_FOUND
        )
    session.delete(user_db)
    session.commit()

    return {'message': 'user deleted'}
