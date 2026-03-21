from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from typing import List

from db.tables import Order, OrderItem, Product
from database import get_db
from CRUD.create import createOrder
from CRUD.update import updateOrder, updateOrderItem
from CRUD.delete import deleteOrder, deleteOrderItem
from db.schemas import OrderItemCreate, OrderItemDisplay, OrderCreate, OrderUpdate, OrderDisplay

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

# Request body schema for updating item quantity
class OrderItemQuantityUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="Must be at least 1")

def getOrders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).options(
        joinedload(Order.order_items).joinedload(OrderItem.product_related)
    ).offset(skip).limit(limit).all()

def getOrder(db: Session, order_id: int):
    return db.query(Order).options(
        joinedload(Order.order_items).joinedload(OrderItem.product_related)
    ).filter(Order.id == order_id).first()

def addItem(db: Session, order_id: int, item_data: OrderItemCreate):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise ValueError(f"Order ID {order_id} not found")

    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise ValueError(f"Product ID {item_data.product_id} not found")

    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.product_id == item_data.product_id
    ).first()

    try:
        if existing_item:
            old_total = existing_item.quantity * existing_item.price_at_order
            existing_item.quantity += item_data.quantity
            new_total = existing_item.quantity * existing_item.price_at_order
            db_order.total_amount += (new_total - old_total)
        else:
            price_at_order = product.price
            new_item = OrderItem(
                order_id=order_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price_at_order=price_at_order
            )
            db.add(new_item)
            db.flush()
            db_order.total_amount += (item_data.quantity * price_at_order)
        db.commit()
        db.refresh(db_order)
        return existing_item or new_item
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Failed to add item: {str(e)}")

@router.post("/", response_model=OrderDisplay, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    try:
        return createOrder(db, order_data)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))

@router.get("/", response_model=List[OrderDisplay])
def get_all_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return getOrders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=OrderDisplay)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    db_order = getOrder(db, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order ID {order_id} not found")
    return db_order

@router.patch("/{order_id}", response_model=OrderDisplay)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    try:
        return updateOrder(db, order_id, order_update)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    try:
        deleteOrder(db, order_id)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))

@router.post("/{order_id}/items", response_model=OrderItemDisplay, status_code=status.HTTP_201_CREATED)
def add_item_to_order(order_id: int, item_data: OrderItemCreate, db: Session = Depends(get_db)):
    try:
        return addItem(db, order_id, item_data)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))

@router.put("/{order_id}/items/{item_id}", response_model=OrderItemDisplay)
def update_order_item(order_id: int, item_id: int, body: OrderItemQuantityUpdate, db: Session = Depends(get_db)):
    try:
        db_item = updateOrderItem(db, order_id, item_id, body.quantity)
        if not db_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found in this order")
        return db_item
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))

@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_order(order_id: int, item_id: int, db: Session = Depends(get_db)):
    try:
        deleteOrderItem(db, order_id, item_id)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))