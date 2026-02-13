from sqlmodel import SQLModel, create_engine, Session

from src.settings import Settings
from src.models import users


def get_session():
    engine = create_engine(url=Settings().DATABASE_URL, echo=True)

    with Session(engine) as session:
        yield session
