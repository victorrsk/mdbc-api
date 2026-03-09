from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.exceptions import (
    EntityAlreadyExistsConflict,
    EntityNotFound,
    NotEnoughPermission,
    UserDataInUse,
    entity_already_exists_conflict_handler,
    entity_not_found_handler,
    not_enough_permission_handler,
    user_data_in_use_handler,
)
from src.routers import auth, authors, books, users

app_description = """
## An experimental REST API
---
- ### Here you have routes to:
    - **users**: `/users`, `/users/user_id`

    - **authors**: `/authors`, `/authors/author_id`

    - **auth**: `/auth/token`

    - **books**: `/books`, `/books/book_id`
"""


def log():
    print('api started')


app = FastAPI(title='My Digital Books Collection API', description=app_description)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)

app.add_exception_handler(UserDataInUse, user_data_in_use_handler)
app.add_exception_handler(
    EntityAlreadyExistsConflict, entity_already_exists_conflict_handler
)
app.add_exception_handler(EntityNotFound, entity_not_found_handler)
app.add_exception_handler(NotEnoughPermission, not_enough_permission_handler)


@app.get('/')
def read_root():
    print(app.exception_handlers)
    return JSONResponse({'message': 'hello world!'}, status_code=200)
