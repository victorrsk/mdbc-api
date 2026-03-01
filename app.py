from fastapi import FastAPI

from src.routers import auth, authors, users

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


@app.get('/')
def read_root():
    return {'message': 'hello world'}
