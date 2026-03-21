from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm.session import Session
from typing import List

from database import get_db
from db.tables import User
from CRUD.create import createUser
from CRUD.delete import deleteUser
from CRUD.update import updateUser
from db.schemas import UserCreate, UserDisplay, UserUpdate

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.post('/', response_model=UserDisplay, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return createUser(db, user_data)
    except ValueError as e:
        status_code = status.HTTP_409_CONFLICT if "already" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=List[UserDisplay])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving users: {str(e)}")

@router.get("/{user_id}", response_model=UserDisplay)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    # No try/except here — avoids accidentally swallowing the 404 HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
    return user

@router.patch("/{user_id}", response_model=UserDisplay)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        return updateUser(db, user_id, user_update)
    except ValueError as e:
        if "not found" in str(e).lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "already taken" in str(e).lower() or "already registered" in str(e).lower():
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating user: {str(e)}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        deleteUser(db, user_id)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting user: {str(e)}")