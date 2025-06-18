from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm.session import Session
from database import get_db
from db.tables import User
from typing import List

from create import createUser
from delete import deleteUser
from update import updateUser

from schemas import UserCreate, UserDisplay, UserUpdate

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def getUser_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def getUser_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def getUsers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

@router.post('/', response_model=UserDisplay, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return createUser(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/", response_model=List[UserDisplay])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return getUsers(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserDisplay)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = getUser_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.patch("/{user_id}", response_model=UserDisplay)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = updateUser(db, user_id, user_update)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = deleteUser(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return