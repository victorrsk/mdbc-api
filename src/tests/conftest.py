import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, StaticPool, create_engine

from app import app
from src.database.session import SQLModel, get_session


@pytest.fixture
def session():
    test_database = 'sqlite:///:memory:'

    engine = create_engine(
        url=test_database,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False},
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def override_session():
        return session

    # overrides production database connection with in memory database
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}
