from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import User

from sqlmodel import Field, Relationship, SQLModel


# TODO: migrations with alembic
class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    created_by_id: int = Field(foreign_key='user.id', ondelete='CASCADE')
    name: str = Field(unique=True)

    user: 'User' = Relationship(back_populates='authors')

    model_config = {'extra': 'allow'}
