from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from src.models.users import User
from src.schemas.schemas import TokenSchema
from src.security import create_access_token, verify_pwd
from src.types import OAuth_form, T_Session

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=TokenSchema, status_code=status.HTTP_200_OK)
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
