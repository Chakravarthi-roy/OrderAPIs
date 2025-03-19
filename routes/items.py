from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from db.tables import Item
from database import get_db

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

def delete_item(db: Session, ps: bool, ds: bool):
    if ps == True and ds == True:
        product = db.query(Item).filter(Item.prep_status==ps, Item.delivery_status==ds).first()
    
    db.delete(product)
    db.commit()
    return 'Deleted'

def get_all_item(db: Session):
    return db.query(Item).all()

@router.get('/orders')
def get_all_items(db: Session = Depends(get_db)):
    return get_all_item(db)

@router.get('/{os}/{ds}')
def delete_items(os: bool, ds: bool, db: Session = Depends(get_db)):
    return delete_item(db, os, ds)