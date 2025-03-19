from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session
from db.tables import Product
from schemas import ProductBase, ProductDisplay
from database import get_db
from create import create_product

router = APIRouter(
    prefix='/products',
    tags=['products']
)

def get_all_products(db: Session):
    return db.query(Product).all()

def update_product(db: Session, p_name: str, request: ProductBase):
    product = db.query(Product).filter(Product.product_name==p_name)
    product.update({
        Product.product_name: request.product_name,
        Product.price: request.price,
        Product.time_req: request.time_req,
        Product.category: request.category,
        Product.description: request.description
    })
    db.commit()
    return 'ok'

def delete_product(db: Session, p_name: str):
    product = db.query(Product).filter(Product.product_name==p_name).first()
    if product:
        db.delete(product)
        db.commit()   
        return 'Deleted'
    else:
        raise HTTPException(status_code=404, detail='Product does not exist')


# create product
@router.post('/', response_model=ProductDisplay)
def create_products(request: ProductBase, db: Session = Depends(get_db)):
    return create_product(db, request)

# Get all products
@router.get('/products', response_model=List[ProductDisplay])
def get_all_product(db: Session = Depends(get_db)):
    return get_all_products(db)

# Update products
@router.post('/{p_name}/update')
def update_products(p_name: str, request: ProductBase, db: Session = Depends(get_db)):
    return update_product(db, p_name, request)

# Delete products
@router.get('/{p_name}/delete')
def delete_products(p_name: str, db: Session = Depends(get_db)):
    return delete_product(db, p_name)