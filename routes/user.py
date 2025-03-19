from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from database import get_db
from db.tables import Signup
from create import create_user
from schemas import UserBase, UserDisplay

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_all_users(db: Session):
    return db.query(Signup).all()

@router.post('/', response_model=UserDisplay)
def create_users(request: UserBase, db: Session = Depends(get_db)):
    return create_user(db, request)