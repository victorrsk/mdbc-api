from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from sqlmodel import select

from src.database.session import T_Session
from src.database.utils import clean_user_data
from src.email_handler import send_email
from src.exceptions import EntityNotFound, NotEnoughPermission, UserDataInUse
from src.models.users import User
from src.rate_limiter import limiter
from src.schemas.schemas import UserIn, UserList, UserOut
from src.security import CurrentUser, get_pwd_hash
from src.settings import Settings
from src.types import T_PositiveInt

# api router for /users endpoints
router = APIRouter(prefix='/users', tags=['users'])

post_description = """
## About user data sanitization:

- ### The username will be converted to lowercase, the blank spaces around the name
    ### gonna be removed and the ones between the username will be replaced by a "-"
- ### The email will have all the blank spaces removed (there isn't a real strong
    ### email validation, only the `Emailstr` type from pydantic)
- ### The password will have all the blank spaces removed (password gonna be hashed)

## About the email:

### In case you put a valid email used by you and all your data is correct, a simple
### sign up confirmation will be send
"""

put_description = """
## About the `put` method:

- ### You can only update (perform a `put` request) yourself.
- ### Every other `user_id` inserted will be treated with `403, Forbidden`
"""

delete_description = """
## About the `delete` method:

- ### You can only delete (perform a `delete` request) yourself
- ### By deleting yourself all the authors related to your id will be deleted (and the
    ### books related to this author)
- ### Even if you didn't created an author but created book(s), all the books related to
    ### your id will be deleted
- ### All the reviews related to your id will be deleted
"""


@router.post(
    '/',
    response_model=UserOut,
    description=post_description,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    req: Request, user: UserIn, session: T_Session, background_tasks: BackgroundTasks
):
    user = clean_user_data(user)
    user.password = get_pwd_hash(user.password)
    user_db = User(
        id=None, username=user.username, email=user.email, password=user.password
    )

    result = session.scalar(
        select(User).where(
            (User.username == user_db.username) | (User.email == user_db.email)
        )
    )
    if result:
        raise UserDataInUse()

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    print('sending email...')
    print(f'email config: sender is {Settings().MAIL_FROM}')
    background_tasks.add_task(send_email, user_db)

    return user_db


@router.get('/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
@limiter.limit('10/minute')
def read_user(
    user_id: T_PositiveInt,
    session: T_Session,
    current_user: CurrentUser,
    request: Request,
):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise EntityNotFound(entity='user')

    return user_db


@router.get('/', response_model=UserList, status_code=status.HTTP_200_OK)
def read_users(session: T_Session):
    users_list = session.scalars(select(User))

    return {'users': users_list}


@router.put(
    '/{user_id}',
    response_model=UserOut,
    description=put_description,
    status_code=status.HTTP_200_OK,
)
def update_user(
    user_id: T_PositiveInt, user: UserIn, session: T_Session, current_user: CurrentUser
):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise NotEnoughPermission()
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='not enough permission'
        )
    user = clean_user_data(user)
    user.password = get_pwd_hash(user.password)

    # verifies if other user uses the same email or username
    test_user = session.scalar(
        select(User).where(
            ((User.username == user.username) | (User.email == user.email))
            & (User.id != user_id)
        )
    )
    if test_user:
        raise UserDataInUse()
    # overrides the actual user data with the received from the api
    user_db.username = user.username
    user_db.email = user.email
    user_db.password = user.password

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    # then returns the same user with the new data
    return user_db


@router.delete(
    '/{user_id}', description=delete_description, status_code=status.HTTP_200_OK
)
def delete_user(user_id: T_PositiveInt, session: T_Session, current_user: CurrentUser):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise EntityNotFound('user')
    if user_id != current_user.id:
        raise NotEnoughPermission()
    session.delete(user_db)
    session.commit()

    return {'message': 'user deleted'}
