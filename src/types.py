from typing import Annotated

from fastapi import Depends, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from src.database.session import get_session

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


T_Session = Annotated[Session, Depends(get_session)]

T_PositiveInt = Annotated[int, Path(gt=0)]

Token = Annotated[str, Depends(oauth_scheme)]

OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
