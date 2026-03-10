from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

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
from src.rate_limiter import limiter
from src.routers import auth, authors, books, users

app_description = """
## An experimental REST API
---
- ### Here you have routes to:
    - **users**: `/users`, `/users/user_id`

    - **authors**: `/authors`, `/authors/author_id`

    - **auth**: `/auth/token`

    - **books**: `/books`, `/books/book_id`, `books/book_id/reviews`,
    `books/reviews/review_id`

- ### Rate limiter:
    - **`authors`, `auth` and `users` have a limit of 20 requests per minute**
        - **The limit is shared beetwen the routes, so for example, making 10 requests**
        **in authors will let you with only 10 more requests**

    - **`books` have a rate limit of 20 requests per 2 minutes**
        - **The limit is shared**
    - **`books/reviews` endpoints have a limit of 10 requests per minute**
        - **The limit is shared**
    - **If you run out of requests just wait until it resets the limiter**
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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)

app.state.limiter = limiter


@app.get('/')
def read_root():
    print(app.exception_handlers)
    return JSONResponse({'message': 'hello world!'}, status_code=200)
