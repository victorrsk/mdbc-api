from sqlmodel import SQLModel, create_engine

from src.settings import Settings
from src.models import users, authors

# FIXME
def get_engine():
    engine = create_engine(url=Settings().DATABASE_URL, echo=True)
    return engine

if __name__ == '__main__':
    engine = get_engine()
    SQLModel.metadata.create_all(bind=engine)


