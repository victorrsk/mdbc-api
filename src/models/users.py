from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .authors import Author
    from .books import Book


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    password: str

    authors: list['Author'] = Relationship(cascade_delete=True, back_populates='user')
    books: list['Book'] = Relationship(cascade_delete=True, back_populates='user')

    # used to allow extra attributes in tests
    model_config = {'extra': 'allow'}
