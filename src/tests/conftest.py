import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, StaticPool, create_engine

from app import app
from src.database.session import SQLModel, get_session
from src.models.users import User


@pytest.fixture
def session():
    test_database = 'sqlite:///:memory:'

    engine = create_engine(
        url=test_database,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False},
    )

    SQLModel.metadata.create_all(engine)

    # yield session for fixtures/functions perform operations in database
    with Session(engine) as session:
        yield session

    # delete tables and close database connection
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session):
    def override_session():
        return session

    # overrides production database connection with in memory database
    app.dependency_overrides[get_session] = override_session
    # returns fastAPI test client
    with TestClient(app) as client:
        yield client

    # clean the dependency
    app.dependency_overrides = {}


@pytest.fixture
def user(session):
    user_ = User(
        id=None, username='test', email='testemail@email.com', password='password123'
    )

    session.add(user_)
    session.commit()
    session.refresh(user_)

    return user_
