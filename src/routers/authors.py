from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from src.database.session import T_Session
from src.database.utils import clean_author_data
from src.models.authors import Author
from src.schemas.schemas import AuthorIn, AuthorOut, AuthorsList
from src.security import CurrentUser
from src.types import T_PositiveInt

router = APIRouter(prefix='/authors', tags=['authors'])


post_description = """
## About author data sanitization

- ### All the blank spaces around the author name gotta be removed and all the ones
    ### between the author name will be replaced by a "-"
"""


@router.post('/', response_model=AuthorOut, description=post_description)
def create_author(author: AuthorIn, current_user: CurrentUser, session: T_Session):
    author = clean_author_data(author)
    _author = session.scalar(select(Author).where(Author.name == author.name))
    if _author:
        raise HTTPException(
            detail='author already exists', status_code=status.HTTP_409_CONFLICT
        )

    author_db = Author(id=None, created_by_id=current_user.id, name=author.name)

    session.add(author_db)
    session.commit()
    session.refresh(author_db)
    author_db.crator_name = current_user.username

    return author_db


@router.get('/{author_id}', response_model=AuthorOut)
def read_author(
    author_id: T_PositiveInt, current_user: CurrentUser, session: T_Session
):
    author = session.scalar(select(Author).where(Author.id == author_id))
    if not author:
        raise HTTPException(
            detail='author not found', status_code=status.HTTP_404_NOT_FOUND
        )
    return author


@router.get('/', response_model=AuthorsList)
def read_authors(current_user: CurrentUser, session: T_Session):
    authors = session.scalars(select(Author))
    return {'authors': authors}


@router.put('/{author_id}', response_model=AuthorOut)
def update_author(
    author: AuthorIn,
    author_id: T_PositiveInt,
    current_user: CurrentUser,
    session: T_Session,
):
    author = clean_author_data(author)

    _author = session.scalar(select(Author).where(Author.id == author_id))
    if not _author:
        raise HTTPException(
            detail='not enough permission', status_code=status.HTTP_403_FORBIDDEN
        )
    if _author.created_by_id != current_user.id:
        raise HTTPException(
            detail='not enough permission', status_code=status.HTTP_403_FORBIDDEN
        )

    auth_exists = session.scalar(
        select(Author).where((Author.name == author.name) & (Author.id != author_id))
    )

    if auth_exists:
        raise HTTPException(
            detail='author already exists', status_code=status.HTTP_409_CONFLICT
        )

    _author.name = author.name

    session.add(_author)
    session.commit()
    session.refresh(_author)

    return _author


@router.delete('/{author_id}')
def delete_author(
    author_id: T_PositiveInt, current_user: CurrentUser, session: T_Session
):
    # just testing this query style
    query = select(Author).where(Author.id == author_id)
    _author = session.scalar(query)
    if not _author:
        raise HTTPException(
            detail='not enough permission', status_code=status.HTTP_403_FORBIDDEN
        )
    if _author.created_by_id != current_user.id:
        raise HTTPException(
            detail='not enough permission', status_code=status.HTTP_403_FORBIDDEN
        )

    session.delete(_author)
    session.commit()

    return {'message': 'author deleted'}
