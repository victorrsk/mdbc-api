from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, unique=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    password: str

    # used to allow extra attributes in tests
    model_config = {'extra': 'allow'}
