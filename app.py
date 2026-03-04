from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.routers import auth, authors, books, users

app_description = """
## An experimental REST API
---
- ### Here you have routes to:
    - **users**: `/users`, `/users/user_id`

    - **authors**: `/authors`, `/authors/author_id`

    - **auth**: `/auth/token`

    - **books**: todo
"""

app = FastAPI(title='My Digital Books Collection API', description=app_description)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)


@app.get('/')
def read_root():
    return JSONResponse({'message': 'hello world!'}, status_code=200)
