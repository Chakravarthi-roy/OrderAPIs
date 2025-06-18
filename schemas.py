from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

#items
class OrderItemBase(BaseModel):
    product_name: str
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemDisplay(OrderItemBase):
    id: int
    order_id: int
    item_price_at_order: Decimal

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    items: List[OrderItemCreate] = []

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    prep_status: Optional[str] = None
    delivery_status: Optional[str] = None

    class Config:
        from_attributes = True

class OrderDisplay(OrderBase):
    order_id: int
    order_time: datetime
    total_amount: Decimal
    prep_status: str
    delivery_status: str
    items: List[OrderItemDisplay] = Field(..., alias="order_items")

    class Config:
        from_attributes = True
        populate_by_name = True


#-------------------------------------------------
#-------------------------------------------------

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

class ProductUpdate(BaseModel):
    price: Optional[Decimal] = Field(None, gt=0, description="Price must be a positive decimal number")
    time_req: Optional[int] = Field(None, gt=0, description="Time required in minutes, if applicable")
    category: Optional[str] = None
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductDisplay(ProductBase):
    class Config:
        from_attributes = True

#-------------------------------------------------
#-------------------------------------------------

#user
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    full_name: Optional[str] = Field(None, max_length=100)
    hostel_no: Optional[int] = None
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=100)
    hostel_no: Optional[int] = None

    class Config:
        from_attributes = True

class UserDisplay(UserBase):
    id: int
    class Config():
        from_attributes = True