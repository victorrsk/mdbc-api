from fastapi import FastAPI

from src.routers import auth, authors, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(authors.router)


@app.get('/')
def read_root():
    return {'message': 'hello world'}
