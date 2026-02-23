from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pwdlib import PasswordHash
from sqlmodel import select

from src.models.users import User
from src.settings import Settings
from src.types import T_Session, Token

pwd_context = PasswordHash.recommended()


# return the user hasdhed pwd
def get_pwd_hash(pwd: str):
    hashed_pwd = pwd_context.hash(pwd)

    return hashed_pwd


def verify_pwd(plain_pwd: str, hashed_pwd: str):
    # returns true if the plain pwd matches de hashed.
    return pwd_context.verify(password=plain_pwd, hash=hashed_pwd)


def create_access_token(data: dict):
    to_encode = data.copy()
    exp_time = datetime.utcnow() + timedelta(
        minutes=Settings().TOKEN_MINUTES_EXPIRE_TIME
    )
    to_encode['exp'] = exp_time

    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=Settings().SECRET_KEY,
        algorithm=Settings().TOKEN_ALGORITHM,
    )

    return encoded_jwt


def get_current_user(token: Token, session: T_Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, Settings().SECRET_KEY, Settings().TOKEN_ALGORITHM)
        sub_email = payload['sub']
        if not sub_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == sub_email))
    if not user:
        raise credentials_exception

    return user
