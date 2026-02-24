from sqlmodel import SQLModel, Field


class Author(SQLModel, table=True):
    id: int | None = Field(primary_key=True, unique=True)
    created_by_id: int = Field(foreign_key=True)
    name: str = Field(unique=True)

    model_config = {'extra': 'allow'}
