from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from src.database.session import T_Session
from src.database.utils import clean_book_data
from src.exceptions import EntityAlreadyExistsConflict, EntityNotFound
from src.models.authors import Author
from src.models.books import Book
from src.schemas.schemas import BookIn, BookList, BookOut
from src.security import CurrentUser
from src.types import T_PositiveInt

router = APIRouter(prefix='/books', tags=['books'])

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


@router.post('/', response_model=BookOut, description=post_description)
def create_book(book: BookIn, session: T_Session, current_user: CurrentUser):

    book = clean_book_data(book)

    author_db = session.scalar(select(Author).where(Author.id == book.author_id))
    book_db = session.scalar(select(Book).where(Book.title == book.title))

    if not author_db:
        raise EntityNotFound('author')
    if book_db:
        raise EntityAlreadyExistsConflict('book')

    create_book = Book(
        title=book.title, year=book.year, author_id=book.author_id, genre=book.genre
    )
    session.add(create_book)
    session.commit()
    session.refresh(create_book)

    return create_book


@router.get('/', response_model=BookList)
def read_books(session: T_Session):
    books = session.scalars(select(Book))

    return {'books': books}


@router.patch('/{book_id}')
def update_book(
    book_id: T_PositiveInt, book: BookIn, current_user: CurrentUser, session: T_Session
):
    book_db = session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise HTTPException(
            detail='book not found', status_code=status.HTTP_404_NOT_FOUND
        )
    # FIXME
    author_db = session.scalar(select(Author).where(Author.id == book_db.author_id))
    if not author_db:
        raise HTTPException(
            detail='author not found', status_code=status.HTTP_404_NOT_FOUND
        )
