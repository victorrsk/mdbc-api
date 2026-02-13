from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from src.database.utils import clean_user_data, search_user
from src.models.users import User
from src.schemas.schemas import UserIn, UserList, UserOut
from src.security import get_pwd_hash
from src.types import T_PositiveInt, T_Session

# api router for /users endpoints
router = APIRouter(prefix='/users', tags=['users'])

# read search_user() definition for its behavior explanation


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
    # raises 404 if user not found
    user_db = search_user(id=user_id, session=session)
    # if the user exists then return
    return user_db


@router.get('/', response_model=UserList)
def read_users(session: T_Session):
    users_list = session.scalars(select(User))

    return {'users': users_list}


@router.put('/{user_id}', response_model=UserOut)
def update_user(user_id: T_PositiveInt, user: UserIn, session: T_Session):
    user = clean_user_data(user)
    user.password = get_pwd_hash(user.password)

    user_db = search_user(id=user_id, session=session)

    test_user = session.scalar(
        select(User).where(
            ((User.username == user.username) | (User.email == user.email))
            & (User.id != user_id)
        )
    )
    if test_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='username or email already in use',
        )
    # overrides the actual user data with the received from the api
    user_db.username = user.username
    user_db.email = user.email
    user_db.password = user.password

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    # then returns the same user with the new data
    return user_db


@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
def delete_user(user_id: T_PositiveInt, session: T_Session):
    user_db = search_user(id=user_id, session=session)
    session.delete(user_db)
    session.commit()

    return {'message': 'user deleted'}
