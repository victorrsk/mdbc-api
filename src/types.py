from typing import Annotated

from fastapi import Depends, Path
from sqlmodel import Session

from src.database.session import get_session

T_Session = Annotated[Session, Depends(get_session)]
T_PositiveInt = Annotated[int, Path(gt=0)]
