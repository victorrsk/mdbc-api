from typing import Annotated

from fastapi import APIRouter, Query, Request, status
from sqlmodel import select

from src.database.session import T_Session
from src.database.utils import clean_book_data
from src.exceptions import (
    EntityAlreadyExistsConflict,
    EntityNotFound,
    NotEnoughPermission,
)
from src.models.authors import Author
from src.models.books import Book
from src.rate_limiter import limiter
from src.schemas.schemas import BookFilter, BookIn, BookList, BookOut, BookPatch
from src.security import CurrentUser
from src.types import T_PositiveInt

router = APIRouter(prefix='/books', tags=['books'])

T_BookFilter = Annotated[BookFilter, Query()]

post_description = """
## About book creation:

- ### The book data will be sanitized the following way:
    -  ### All the blank spaces around the book name gonna be removed and the
        ### ones beetwen the book name will be replaced by a "-"
- ### You can only create a book with a valid author:
    - ### An existent author
- ### Book names are unique
- ### Before creating a book you can check the authors list at
    ### `GET Read Authors /authors`
- ### You can check the genre options at the schema example here in the docs
    - ### An invalid genre will result in a error
- ### The book year MUST have to be greater or equal to 0
    ### (i'm not considerind old books, like the ones thousands of years B.C)
"""

get_description = """
## Search for specific books with these filters (they're all optional)

- ### `creator_name` means the user who created the book in the system,
    ### not the author.
"""

patch_description = """
## About the `patch` method in books:

- ### By using the `patch` method instead of `put` you can update only desired
    ### data from the book
    - ### The only data you need to always send is the `author_id`
- ### You can only update a book created by you (the current authenticated user)
- ### You can only update a book by providing a valid author_id (an existent author)
- ### The other rules about year, title, data sanitization and genre specified in the
    ### `post` description are also applicable here
"""

delete_description = """
## About the `delete` method in books:

- ### You can only delete books created by you (the current authenticated user)
- ### You can only delete a book by providing a valid book_id
"""


@router.post(
    '/',
    response_model=BookOut,
    description=post_description,
    status_code=status.HTTP_201_CREATED,
)
@limiter.shared_limit('20/2minute', scope='books')
def create_book(
    book: BookIn, session: T_Session, current_user: CurrentUser, request: Request
):

    book = clean_book_data(book)

    author_db = session.scalar(select(Author).where(Author.id == book.author_id))
    book_db = session.scalar(select(Book).where(Book.title == book.title))

    if not author_db:
        raise EntityNotFound('author')
    if book_db:
        raise EntityAlreadyExistsConflict('book')

    create_book = Book(
        title=book.title,
        year=book.year,
        author_id=book.author_id,
        genre=book.genre,
        creator_id=current_user.id,
        creator_name=current_user.username,
    )
    session.add(create_book)
    session.commit()
    session.refresh(create_book)

    return create_book


@router.get(
    '/',
    response_model=BookList,
    status_code=status.HTTP_200_OK,
    description=get_description,
)
@limiter.shared_limit('20/2minute', scope='books')
def read_books(session: T_Session, book_filter: T_BookFilter, request: Request):
    """
    if filters are received, then this for loop will build a query based on the
    values received from the filter

    - offset & limit are exluded because the cleanest way to add them is explicitly
    in the final query

    - if you have doubts about how the T_BookFilter is built, check the schemas file
    (line 104)
    """
    query = select(Book)

    for field, value in book_filter.model_dump(
        exclude_unset=True, exclude={'offset', 'limit'}
    ).items():
        if book_filter.genre:
            query = query.where(Book.genre == book_filter.genre)

        if book_filter.author_id:
            query = query.where(Book.author_id == book_filter.author_id)

        if not isinstance(value, int):
            clean_value = value.strip().lower().replace(' ', '-')
            column = getattr(Book, field)
            query = query.filter(column.contains(clean_value))

    books = session.scalars(query.offset(book_filter.offset).limit(book_filter.limit))

    return {'books': books}


@router.get('/{book_id}', response_model=BookOut, status_code=status.HTTP_200_OK)
@limiter.shared_limit('20/2minute', scope='books')
def read_book(session: T_Session, book_id: T_PositiveInt, request: Request):
    book_db = session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise EntityNotFound('book')

    return book_db


@router.patch(
    '/{book_id}',
    response_model=BookOut,
    status_code=status.HTTP_200_OK,
    description=patch_description,
)
@limiter.shared_limit('20/2minute', scope='books')
def update_book(
    book_id: T_PositiveInt,
    book: BookPatch,
    current_user: CurrentUser,
    session: T_Session,
    request: Request,
):
    if book.title:
        book = clean_book_data(book)
    book_db = session.scalar(select(Book).where(Book.id == book_id))
    book_title = session.scalar(select(Book).where(Book.title == book.title))
    author_exists = session.scalar(select(Author).where(Author.id == book.author_id))
    if not book_db:
        raise EntityNotFound('book')
    if not author_exists:
        raise EntityNotFound('author')
    if book_db.creator_id != current_user.id:
        raise NotEnoughPermission
    if book_title:
        raise EntityAlreadyExistsConflict('book')
    # exclude unset fields, the ones setted/updated will overwrite their old values
    for attr, value in book.model_dump(exclude_unset=True).items():
        setattr(book_db, attr, value)

    session.add(book_db)
    session.commit()
    session.refresh(book_db)

    return book_db


@router.delete(
    '/{book_id}', status_code=status.HTTP_200_OK, description=delete_description
)
@limiter.shared_limit('20/2minute', scope='books')
def delete_book(
    current_user: CurrentUser,
    session: T_Session,
    book_id: T_PositiveInt,
    request: Request,
):
    book_db = session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise EntityNotFound('book')
    if book_db.creator_id != current_user.id:
        raise NotEnoughPermission()

    session.delete(book_db)
    session.commit()

    return {'message': 'book deleted'}
