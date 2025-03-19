from typing import Optional
from pydantic import BaseModel

#items
class ItemBase(BaseModel):
    item_name: str
    customer_name: str
    quantity: int

class ItemDisplay(BaseModel):
    item_name: str
    customer_name: str
    quantity: int
    prep_status: bool
    delivery_status: bool

    class Config:
        from_attributes = True

#products
class Image(BaseModel):
    url: str
    alias: str

class ProductBase(BaseModel):
    product_name: str
    price: int
    time_req: int
    category: str
    description: str | None = None
    image: Optional[Image] = None

class ProductDisplay(BaseModel):
    product_name: str
    category: str
    price: int
    class Config:
        from_attributes = True

#user
class UserBase(BaseModel):
    email: str
    password: str
    
class UserDisplay(BaseModel):
    email: str
    class Config():
        from_attributes = True