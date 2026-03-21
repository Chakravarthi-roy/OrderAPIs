from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError

from db.tables import Product
from database import get_db
from CRUD.create import createProduct
from CRUD.delete import deleteProduct
from CRUD.update import updateProduct
from db.schemas import ProductCreate, ProductUpdate, ProductDisplay

router = APIRouter(
    prefix='/products',
    tags=['products']
)

def getProducts(db: Session):
    return db.query(Product).all()

def getProduct(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

@router.post("/", response_model=ProductDisplay, status_code=status.HTTP_201_CREATED)
def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    try:
        return createProduct(db, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/", response_model=List[ProductDisplay])
def get_all_products(db: Session = Depends(get_db)):
    return getProducts(db)

@router.get("/{product_id}", response_model=ProductDisplay)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    db_product = getProduct(db, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found")
    return db_product

@router.patch("/{product_id}", response_model=ProductDisplay)
def update_product(product_id: int, request: ProductUpdate, db: Session = Depends(get_db)):
    try:
        return updateProduct(db, product_id, request)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        deleteProduct(db, product_id)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
