from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=200, examples=['john'])
    email: EmailStr = Field(examples=['myemail@email.com'])
    # model_config = ConfigDict(from_attributes=True)


class UserIn(UserSchema):
    password: str = Field(min_length=8, max_length=200, examples=['mysecretpwd123'])


class UserOut(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserOut]


class TokenSchema(BaseModel):
    token_type: str
    access_token: str


class AuthorIn(BaseModel):
    name: str = Field(examples=['Aditya Bhargava'])


class AuthorOut(AuthorIn):
    id: int
    created_by_id: int


class AuthorsList(BaseModel):
    authors: list[AuthorOut]


class BookGenres(str, Enum):
    FANTASY = 'fantasy'
    ROMANCE = 'romance'
    PHILOSOPHY = 'philosopy'
    TERROR = 'terror'
    HORROR = 'horror'
    COMEDY = 'comedy'
    SOCIOLOGY = 'sociology'
    SCIFI = 'scifi'
    TECHNOLOGY = 'technology'
    PHYSICS = 'physics'
    MATH = 'math'
    CHEMESTRY = 'chemestry'
    POETRY = 'poetry'
    DRAMA = 'drama'
    MISTERY = 'mistery'
    BIOGRAPHY = 'biography'
    ADVENTURE = 'adventure'
    SUSPENSE = 'suspense'


class BookSchema(BaseModel):
    title: str = Field(examples=['Grokking Algorithms'])
    year: int = Field(ge=0, examples=[2016])
    author_id: int = Field(gt=0)
    genre: BookGenres = Field(examples=[BookGenres.TECHNOLOGY])


class BookIn(BookSchema):
    pass


class BookOut(BookSchema):
    id: int


class BookList(BaseModel):
    books: list[BookOut]
