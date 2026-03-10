from typing import Literal

from fastapi import Request
from fastapi import status as st
from fastapi.responses import JSONResponse


class UserDataInUse(Exception):
    def __init__(self):
        pass


def user_data_in_use_handler(exc: UserDataInUse, req: Request):
    return JSONResponse(
        status_code=st.HTTP_409_CONFLICT,
        content={'detail': 'username or email already in use'},
    )


class EntityAlreadyExistsConflict(Exception):
    def __init__(self, entity: Literal['author', 'book', 'review']):
        self.entity = entity


def entity_already_exists_conflict_handler(
    req: Request, exc: EntityAlreadyExistsConflict
):
    return JSONResponse(
        status_code=st.HTTP_409_CONFLICT,
        content={'detail': f'{exc.entity} already exists'},
    )


class EntityNotFound(Exception):
    def __init__(self, entity: Literal['author', 'book', 'user', 'review']):
        self.entity = entity


def entity_not_found_handler(req: Request, exc: EntityNotFound):
    return JSONResponse(
        status_code=st.HTTP_404_NOT_FOUND, content={'detail': f'{exc.entity} not found'}
    )


class NotEnoughPermission(Exception):
    def __init__(self):
        pass


def not_enough_permission_handler(req: Request, exc: NotEnoughPermission):
    return JSONResponse(
        status_code=st.HTTP_403_FORBIDDEN, content={'detail': 'not enough permission'}
    )
