from src.schemas.schemas import UserIn, AuthorIn, BookIn, BookPatch
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

def clean_book_data(book: BookIn | BookPatch):
    # type checker will probably bother you with the red line under lower method
    # but don't worry, it will not cause runtime error
    book.title = book.title.lower().strip().replace(' ', '-')

    return book
