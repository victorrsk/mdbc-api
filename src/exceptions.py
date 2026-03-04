from typing import Literal

from fastapi import HTTPException
from fastapi import status as st


class UserDataInUse(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=st.HTTP_409_CONFLICT, detail='username or email already in use'
        )


class EntityAlreadyExistsConflict(HTTPException):
    def __init__(
        self,
        entity: Literal['author', 'book'],
    ):
        if entity == 'author':
            detail = 'author already exists'
        elif entity == 'book':
            detail = 'book already exists'

        super().__init__(status_code=st.HTTP_409_CONFLICT, detail=detail)


class EntityNotFound(HTTPException):
    def __init__(self, entity: Literal['author', 'book', 'user']):
        if entity == 'user':
            detail = 'user not found'
        elif entity == 'author':
            detail = 'author not found'
        elif entity == 'book':
            detail = 'book not found'
        super().__init__(status_code=st.HTTP_404_NOT_FOUND, detail=detail)


class NotEnoughPermission(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=st.HTTP_403_FORBIDDEN, detail='not enough permission'
        )
