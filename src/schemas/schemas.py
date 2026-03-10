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
    creator_id: int
    creator_name: str


class AuthorsList(BaseModel):
    authors: list[AuthorOut]


class BookGenres(str, Enum):
    FANTASY = 'fantasy'
    ROMANCE = 'romance'
    PHILOSOPHY = 'philosophy'
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


class BookPatch(BaseModel):
    title: str | None = Field(
        default=None, examples=['Grokking Algorithms'], min_length=3
    )
    year: int | None = Field(ge=0, default=None, examples=[2016])
    author_id: int = Field(gt=0)
    genre: BookGenres | None = Field(default=None, examples=[BookGenres.TECHNOLOGY])


class BookIn(BookSchema):
    pass


class BookOut(BookSchema):
    id: int
    creator_id: int
    creator_name: str


class BookList(BaseModel):
    books: list[BookOut]


class Filter(BaseModel):
    offset: int = 0
    limit: int = 10


class AuthorFilter(Filter):
    name: str | None = Field(
        default=None, description='**search an author by his name**'
    )
    creator_name: str | None = Field(
        default=None,
        description='**search an author by his creator name**',
    )


class BookFilter(Filter):
    genre: BookGenres | None = Field(
        default=None, description='**search an book based on its genre**'
    )
    title: str | None = Field(
        default=None, description='**search an book by its name**'
    )
    creator_name: str | None = Field(
        default=None, description='**search an book by its creator name**'
    )
    author_id: int | None = Field(
        default=None, gt=0, description='**search an books by its author id**'
    )


class BookReviewIn(BaseModel):
    comment: str = Field(
        min_length=10, max_length=200, examples=['This book is awesome!']
    )


class BookReviewOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: str
    comment: str


class BookReviewList(BaseModel):
    reviews: list[BookReviewOut]
