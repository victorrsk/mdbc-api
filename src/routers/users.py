from fastapi import APIRouter, status
from pwdlib import PasswordHash

from schemas.schemas import UserIn, UserOut

router = APIRouter(prefix='/users', tags=['users'])


users = []

pwd_context = PasswordHash.recommended()


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn):
    # sanitizing user input
    user.id = len(users) + 1
    user.username = user.username.lower().replace(' ', '')
    user.email = user.email.replace(' ', '')
    user.password = user.password.replace(' ', '')
    user.password = pwd_context.hash(user.password)
    # inserting after data cleanup
    for user_ in users:
        if user.username == user_.username or user.email == user_.email:
            return {'err': 'email or username in use'}
    users.append(user)
    return user


@router.get('/')
def read_users():
    return users
