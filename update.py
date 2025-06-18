from sqlalchemy.orm.session import Session
from schemas import OrderUpdate, ProductUpdate
from db.tables import Order, OrderItem, Product

def updateProduct(db: Session, p_name: str, request: ProductUpdate):
    db_product = db.query(Product).filter(Product.product_name == p_name).first()
    if not db_product:
        return None

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

def updateOrder(db: Session, order_id: int, order_update: OrderUpdate):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if not db_order:
        return None

    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def updateOrderItem(db: Session, order_id: int, item_id: int, new_quantity: int):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if not db_order:
        raise ValueError(f"Order with ID {order_id} not found.")

    db_item = db.query(OrderItem).filter(OrderItem.id == item_id, OrderItem.order_id == order_id).first()
    if not db_item:
        return None

    old_total_contribution = db_item.quantity * db_item.item_price_at_order
    db_item.quantity = new_quantity
    new_total_contribution = db_item.quantity * db_item.item_price_at_order

    db_order.total_amount = db_order.total_amount - old_total_contribution + new_total_contribution

    db.commit()
    db.refresh(db_item)
    db.refresh(db_order)
    return db_item