from src.schemas.schemas import UserIn, AuthorIn, BookIn
from fastapi import HTTPException, status
from src.database.session import T_Session
from src.models.users import User

from sqlmodel import select

def clean_user_data(user: UserIn):
    user.username = user.username.lower().strip().replace(' ', '-')
    user.email = user.email.replace(' ', '')
    user.password = user.password.replace(' ', '')

    return user

def clean_author_data(author: AuthorIn):
    author.name = author.name.lower().strip().replace(' ', '-')

    return author

def clean_book_data(book: BookIn):
    book.title = book.title.lower().strip().replace(' ', '-')

    return book


def search_user(id: int, session: T_Session):
    """_summary_

    Args:
        id (int): the user id to be searched
        session (T_Session): a session to interact with database

    Raises:
        HTTPException: user not found

    Returns:
        User: user from database
    """
    user = session.scalar(select(User).where(User.id == id))

    if not user:
        raise HTTPException(detail='user not found', status_code=status.HTTP_404_NOT_FOUND)

    return user

