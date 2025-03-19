from sqlalchemy.orm import Session
from db.tables import Product, Signup
from schemas import ProductBase, UserBase
from hash import Hash

def create_product(db: Session, request = ProductBase):
    db_product = Product(
        product_name = request.product_name,
        price = request.price,
        time_req = request.time_req,
        category = request.category,
        description = request.description
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_user(db: Session, request = UserBase):
    new_user = Signup(
        email = request.email,
        hashed_password = Hash.bcrypt(request.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
