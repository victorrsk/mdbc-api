from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from src.database.session import T_Session
from src.models.users import User
from src.schemas.schemas import TokenSchema
from src.security import create_access_token, verify_pwd
from src.types import OAuthForm

router = APIRouter(prefix='/auth', tags=['auth'])


auth_description = """
## About authentication:

- ### The authentication flow uses the user email and password to generate a token (JWT)
    - ### Altought the auth form asks for the `username` the logic behind the auth flow
        ### uses the user email, otherwise you'll do not get authenticated
- ### The JWT have a 60 minutes expire time
- ### The claims used in the JWT are:
    1. `sub` - the user email
    2. `exp` - the expire time
"""


@router.post(
    '/token',
    response_model=TokenSchema,
    description=auth_description,
    status_code=status.HTTP_200_OK,
)
def login_for_access_token(form_data: OAuthForm, session: T_Session):
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
    # if all the user credentials are valid then returns the token
    access_token = create_access_token(data={'sub': user_db.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
