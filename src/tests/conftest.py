import pytest
from factory.base import Factory
from factory.declarations import LazyAttribute, Sequence
from fastapi.testclient import TestClient
from sqlmodel import Session, StaticPool, create_engine

from app import app
from src.database.session import SQLModel, get_session
from src.models.authors import Author
from src.models.users import User
from src.security import get_pwd_hash

# tests factories --------------------------------------------------------


class RandomUser(Factory):
    class Meta:
        model = User

    username = Sequence(lambda num: f'test{num}')
    email = LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = LazyAttribute(lambda obj: f'{obj.username}_password')


class RandomAuthor(Factory):
    class Meta:
        model = Author

    name = Sequence(lambda num: f'author{num}')
    # hard coded
    created_by_id = 1


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
    # creates a user with mocked/fake data from factory
    _user = RandomUser()
    clean_pwd = _user.password
    _user.password = get_pwd_hash(clean_pwd)

    session.add(_user)
    session.commit()
    session.refresh(_user)
    # creates an clean_pwd attr to use the plain pwd in tests
    setattr(_user, 'clean_pwd', clean_pwd)

    return _user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': user.clean_pwd}
    )

    _token = response.json()['access_token']

    return _token


@pytest.fixture
def author(user, session):
    _author = RandomAuthor()

    session.add(_author)
    session.commit()
    session.refresh(_author)

    return _author
