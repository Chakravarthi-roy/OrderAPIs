from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from db.tables import Product
from database import get_db
from create import createProduct
from delete import deleteProduct
from update import updateProduct
from schemas import (
    ProductCreate, 
    ProductUpdate, 
    ProductDisplay
)

router = APIRouter(
    prefix='/products',
    tags=['products']
)       

def getProducts(db: Session):
    return db.query(Product).all()

def getProduct(db: Session, product_name: str):
    return db.query(Product).filter(Product.product_name == product_name).first()


# create product routes
@router.post("/", response_model=ProductDisplay, status_code=status.HTTP_201_CREATED)
def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    try:
        return createProduct(db, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[ProductDisplay])
def get_all_products(db: Session = Depends(get_db)):
    return getProducts(db)

@router.get("/{product_name}", response_model=ProductDisplay)
def get_product_by_name(product_name: str, db: Session = Depends(get_db)):
    db_product = getProduct(db, product_name)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product '{product_name}' not found")
    return db_product

@router.patch("/{product_name}", response_model=ProductDisplay)
def update_product(product_name: str, request: ProductUpdate, db: Session = Depends(get_db)):
    db_product = updateProduct(db, product_name, request)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product '{product_name}' not found")
    return db_product

@router.delete("/{product_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_name: str, db: Session = Depends(get_db)):
    db_product = deleteProduct(db, product_name)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product '{product_name}' not found")
    return
