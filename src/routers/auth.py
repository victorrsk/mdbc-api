from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from src.models.users import User
from src.security import verify_pwd
from src.settings import Settings
from src.types import T_Session

router = APIRouter(prefix='/auth', tags=['auth'])

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

Token = Annotated[str, Depends(oauth_scheme)]

OAuth_form = Annotated[OAuth2PasswordRequestForm, Depends()]


def create_access_token(data: dict):
    to_encode = data.copy()
    exp_time = datetime.utcnow() + timedelta(minutes=Settings.TOKEN_MINUTES_EXPIRE_TIME)
    to_encode['exp'] = exp_time

    encoded_jwt = jwt.encode(
        payload=to_encode, key=Settings.SECRET_KEY, algorithm=Settings.TOKEN_ALGORITHM
    )

    return encoded_jwt


@router.post('/token')
def login_for_access_token(form_data: OAuth_form, session: T_Session):
    user_db = session.scalar(select(User).where(User.email == form_data.username))
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='could not validate credentials',
        )

    if not verify_pwd(plain_pwd=form_data.password, hashed_pwd=user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='could not validate credentials',
        )

    access_token = create_access_token(data={'sub': user_db.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
