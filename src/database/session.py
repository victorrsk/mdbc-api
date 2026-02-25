from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event

from src.settings import Settings
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

engine = create_engine(url=Settings().DATABASE_URL, echo=True)

@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_session():
    with Session(engine) as session:
        yield session


T_Session = Annotated[Session, Depends(get_session)]