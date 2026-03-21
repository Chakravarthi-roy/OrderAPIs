from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Status enums for validation
class PrepStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"

# ------------------- Order Schemas -------------------
class OrderItemBase(BaseModel):
    product_id: int = Field(..., gt=0, description="Must reference existing product")
    quantity: int = Field(..., gt=0, description="Must be at least 1")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemDisplay(OrderItemBase):
    id: int
    order_id: int
    price_at_order: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int = Field(..., gt=0, description="Must reference existing user")

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="At least one item required")

class OrderUpdate(BaseModel):
    prep_status: Optional[PrepStatus] = None
    delivery_status: Optional[DeliveryStatus] = None

    class Config:
        from_attributes = True

class OrderDisplay(OrderBase):
    id: int
    order_time: datetime
    total_amount: Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]
    prep_status: PrepStatus
    delivery_status: DeliveryStatus
    order_items: List[OrderItemDisplay]

    class Config:
        from_attributes = True

# ------------------- Product Schemas -------------------
class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=100)
    price: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    time_req: Optional[int] = Field(None, gt=0, description="Preparation time in minutes")
    category: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]] = None
    time_req: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class ProductCreate(ProductBase):
    time_req: int = Field(..., gt=0, description="Preparation time in minutes")

class ProductDisplay(ProductBase):
    id: int

    class Config:
        from_attributes = True

# ------------------- User Schemas -------------------
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    hostel_no: Optional[int] = Field(None, ge=1, le=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if (not any(c.islower() for c in v) or
            not any(c.isupper() for c in v) or
                not any(c.isdigit() for c in v)):
            raise ValueError('Password must contain at least one lowercase letter, one uppercase letter, and one digit')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    hostel_no: Optional[int] = Field(None, ge=1, le=20)

    class Config:
        from_attributes = True

class UserDisplay(UserBase):
    id: int

    class Config:
        from_attributes = True