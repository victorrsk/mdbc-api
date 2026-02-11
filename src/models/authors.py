from sqlmodel import Field, SQLModel


class Author(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
