from typing import Annotated

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from models import Users
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['users']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/users', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id', -1)).first()


@router.put('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          new_password: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id', -1)).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')
    user_model.hashed_passwd = bcrypt_context.hash(new_password)

    db.add(user_model)
    db.commit()