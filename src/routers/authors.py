from fastapi import APIRouter

from src.database.session import T_Session
from src.schemas.schemas import AuthorIn, AuthorOut
from src.security import CurrentUser
from src.models.authors import Author

router = APIRouter(prefix='/authors', tags=['authors'])


@router.post('/', response_model=AuthorOut)
def create_author(author: AuthorIn, current_user: CurrentUser, session: T_Session):
    author_db = Author(id=None, created_by_id=current_user.id, name=author.name)

    session.add(author_db)
    session.commit()
    session.refresh(author_db)
    author_db.crator_name = current_user.username

    return author_db
