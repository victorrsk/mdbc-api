from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .authors import Author
    from .reviews import Review
    from .users import User

from sqlmodel import Field, Relationship, SQLModel

from src.schemas.schemas import BookGenres


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, unique=True)
    year: int = Field(nullable=False)
    author_id: int = Field(nullable=False, foreign_key='author.id', ondelete='CASCADE')
    creator_id: int = Field(nullable=False, foreign_key='user.id', ondelete='CASCADE')
    creator_name: str = Field(nullable=False)
    genre: BookGenres = Field(nullable=False)

    author: 'Author' = Relationship(back_populates='books')
    user: 'User' = Relationship(back_populates='books')
    reviews: list[Review] = Relationship(back_populates='book', cascade_delete=True)

    model_config = {'extra': 'ignore'}
