from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .books import Book
    from .users import User

from sqlmodel import Field, Relationship, SQLModel


class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    creator_id: int = Field(nullable=False, foreign_key='user.id', ondelete='CASCADE')
    creator_name: str = Field(nullable=False)
    name: str = Field(unique=True)

    books: list['Book'] = Relationship(back_populates='author', cascade_delete=True)
    user: 'User' = Relationship(back_populates='authors')

    model_config = {'extra': 'allow'}
