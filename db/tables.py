from sqlalchemy import Boolean, Column, Integer, String, Time, ForeignKey
from database import Base


class Signup(Base):
    __tablename__ = "signup"

    email = Column(String, primary_key=True)
    hashed_password = Column(String)

class Product(Base):
    __tablename__ = "products"

    product_name = Column(String, primary_key=True)
    price = Column(Integer)
    time_req = Column(Integer)
    category = Column(String)
    description = Column(String)

class Item(Base):
    __tablename__ = "items"

    item_name = Column(String, ForeignKey('products.product_name'))
    quantity = Column(Integer)
    customer_name = Column(String, primary_key=True)
    order_time = Column(Time("HH:MM:SS"))
    prep_status = Column(Boolean, default=False)
    delivery_status = Column(Boolean, default=False)