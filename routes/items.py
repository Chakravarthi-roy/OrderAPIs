from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from db.tables import Order, OrderItem, Product
from database import get_db
from typing import List, Optional
from create import createOrder
from update import updateOrder, updateOrderItem
from delete import deleteOrder, deleteOrderItem

from schemas import (
    OrderItemCreate, OrderItemDisplay,
    OrderCreate, OrderUpdate, OrderDisplay,
)

router = APIRouter(
    prefix='/products',
    tags=['products']
)

def getOrders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).options(joinedload(Order.order_items)).offset(skip).limit(limit).all()

def getOrder(db: Session, order_id: int):
    return db.query(Order).options(joinedload(Order.order_items)).filter(Order.order_id == order_id).first()


def addItem(db: Session, order_id: int, item_data: OrderItemCreate):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if not db_order:
        raise ValueError(f"Order with ID {order_id} not found.")

    product = db.query(Product).filter(Product.product_name == item_data.product_name).first()
    if not product:
        raise ValueError(f"Product '{item_data.product_name}' not found.")

    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.product_name == item_data.product_name
    ).first()

    if existing_item:
        existing_item.quantity += item_data.quantity
        db.add(existing_item)
        db_order.total_amount += (item_data.quantity * existing_item.item_price_at_order)
        db.commit()
        db.refresh(existing_item)
        db.refresh(db_order)
        return existing_item
    else:
        db_order_item = OrderItem(
            order_id=order_id,
            product_name=item_data.product_name,
            quantity=item_data.quantity,
            item_price_at_order=product.price
        )
        db.add(db_order_item)
        db.commit()
        db.refresh(db_order_item)
        
        db_order.total_amount += (db_order_item.quantity * db_order_item.item_price_at_order)
        db.commit()
        db.refresh(db_order)
        return db_order_item

# Routes

@router.post("/", response_model=OrderDisplay, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    try:
        return createOrder(db, order_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[OrderDisplay])
def get_all_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return getOrders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=OrderDisplay)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    db_order = getOrder(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order

@router.patch("/{order_id}", response_model=OrderDisplay)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    db_order = updateOrder(db, order_id, order_update)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = deleteOrder(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return

@router.post("/{order_id}/items", response_model=OrderItemDisplay, status_code=status.HTTP_201_CREATED)
def add_item_to_order(order_id: int, item_data: OrderItemCreate, db: Session = Depends(get_db)):
    try:
        return addItem(db, order_id, item_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        raise e

@router.put("/{order_id}/items/{item_id}", response_model=OrderItemDisplay)
def update_order_item(order_id: int, item_id: int, new_quantity: int, db: Session = Depends(get_db)):
    try:
        db_item = updateOrderItem(db, order_id, item_id, new_quantity)
        if db_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found in this order")
        return db_item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_order(order_id: int, item_id: int, db: Session = Depends(get_db)):
    try:
        db_item = deleteOrderItem(db, order_id, item_id)
        if db_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found in this order")
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))