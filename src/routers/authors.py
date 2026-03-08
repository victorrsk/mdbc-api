from typing import Annotated

from fastapi import APIRouter, Query, status
from sqlmodel import select

from src.database.session import T_Session
from src.database.utils import clean_author_data
from src.exceptions import (
    EntityAlreadyExistsConflict,
    EntityNotFound,
    NotEnoughPermission,
)
from src.models.authors import Author
from src.schemas.schemas import AuthorFilter, AuthorIn, AuthorOut, AuthorsList
from src.security import CurrentUser
from src.types import T_PositiveInt

router = APIRouter(prefix='/authors', tags=['authors'])

T_AuthorFilter = Annotated[AuthorFilter, Query()]

post_description = """
## About author data sanitization:

- ### All the blank spaces around the author name gonna be removed and all the ones
    ### between the author name will be replaced by a "-"
"""

get_description = """
## Search for specific authors with these filters (they're all optional)
"""

put_description = """
## About the `put` method in authors:

- ### You can only update an author created by you (the current authenticated user)
"""

delete_description = """
## About the `delete` method in authors:

- ### You can only delete an author created by you (the current authenticated user)
- ### By deleting an author all the books related to its id will be deleted" too
"""


@router.post(
    '/',
    response_model=AuthorOut,
    description=post_description,
    status_code=status.HTTP_201_CREATED,
)
def create_author(author: AuthorIn, current_user: CurrentUser, session: T_Session):
    author = clean_author_data(author)
    _author = session.scalar(select(Author).where(Author.name == author.name))
    if _author:
        raise EntityAlreadyExistsConflict(entity='author')

    author_db = Author(
        id=None,
        creator_id=current_user.id,
        creator_name=current_user.username,
        name=author.name,
    )

    session.add(author_db)
    session.commit()
    session.refresh(author_db)

    return author_db


@router.get('/{author_id}', response_model=AuthorOut, status_code=status.HTTP_200_OK)
def read_author(
    author_id: T_PositiveInt, current_user: CurrentUser, session: T_Session
):
    author = session.scalar(select(Author).where(Author.id == author_id))
    if not author:
        raise EntityNotFound('author')
    return author


@router.get('/', response_model=AuthorsList, status_code=status.HTTP_200_OK)
def read_authors(session: T_Session, author_filter: T_AuthorFilter):
    """
    if filters are received, then this for loop will build a query based on the values
    received from the filter

    - offset & limit are exluded because the cleanest way to add them is explicitly in
    the final query

    - if you have doubts about how the T_AuthorFilter is built, check the schemas file
    (line 99)
    """
    query = select(Author)

    for filter, value in author_filter.model_dump(
        exclude_unset=True, exclude={'offset', 'limit'}
    ).items():
        clean_value = value.strip().lower().replace(' ', '-')
        column = getattr(Author, filter)
        query = query.filter(column.contains(clean_value))

    authors = session.scalars(
        query.offset(author_filter.offset).limit(author_filter.limit)
    )

    return {'authors': authors}


@router.put(
    '/{author_id}',
    response_model=AuthorOut,
    description=put_description,
    status_code=status.HTTP_200_OK,
)
def update_author(
    author: AuthorIn,
    author_id: T_PositiveInt,
    current_user: CurrentUser,
    session: T_Session,
):
    author = clean_author_data(author)

    _author = session.scalar(select(Author).where(Author.id == author_id))
    if not _author:
        raise NotEnoughPermission()
    if _author.creator_id != current_user.id:
        raise NotEnoughPermission()

    author_exists = session.scalar(
        select(Author).where((Author.name == author.name) & (Author.id != author_id))
    )

    if author_exists:
        raise EntityAlreadyExistsConflict(entity='author')

    _author.name = author.name

    session.add(_author)
    session.commit()
    session.refresh(_author)

    return _author


@router.delete(
    '/{author_id}', description=delete_description, status_code=status.HTTP_200_OK
)
def delete_author(
    author_id: T_PositiveInt, current_user: CurrentUser, session: T_Session
):
    # just testing this query style
    query = select(Author).where(Author.id == author_id)
    _author = session.scalar(query)
    if not _author:
        raise NotEnoughPermission()
    if _author.creator_id != current_user.id:
        raise NotEnoughPermission()

    session.delete(_author)
    session.commit()

    return {'message': 'author deleted'}
