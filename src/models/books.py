from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .authors import Author

from sqlmodel import Field, Relationship, SQLModel

from src.schemas.schemas import BookGenres


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, unique=True)
    year: int = Field(nullable=False)
    author_id: int = Field(nullable=False, foreign_key='author.id', ondelete='CASCADE')
    genre: BookGenres = Field(nullable=False)

    author: 'Author' = Relationship(back_populates='books')

    model_config = {'extra': 'ignore'}
