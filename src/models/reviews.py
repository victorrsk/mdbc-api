from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .books import Book
    from .users import User


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(nullable=False, foreign_key='book.id', ondelete='CASCADE')
    book_title: str = Field(nullable=False)
    user_id: int = Field(nullable=False, foreign_key='user.id', ondelete='CASCADE')
    comment: str = Field(nullable=False)

    user: 'User' = Relationship(back_populates='reviews')
    book: 'Book' = Relationship(back_populates='reviews')
