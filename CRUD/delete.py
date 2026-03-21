from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from db.tables import Order, OrderItem, Product, User

def deleteProduct(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise ValueError(f"Product ID {product_id} not found")
    try:
        db.delete(db_product)
        db.commit()
        return db_product
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Delete failed: {e.orig}") from e

def deleteOrder(db: Session, order_id: int):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise ValueError(f"Order ID {order_id} not found")
    try:
        db.delete(db_order)
        db.commit()
        return db_order
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Delete failed: {e.orig}") from e

def deleteOrderItem(db: Session, order_id: int, item_id: int):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise ValueError(f"Order ID {order_id} not found")
    db_item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.order_id == order_id
    ).first()
    if not db_item:
        raise ValueError(f"Order item ID {item_id} not found in order {order_id}")
    try:
        item_total = db_item.quantity * db_item.price_at_order
        db.delete(db_item)
        db_order.total_amount -= item_total
        db.commit()
        db.refresh(db_order)
        return db_item
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Delete failed: {e.orig}") from e

def deleteUser(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise ValueError(f"User ID {user_id} not found")
    try:
        db.delete(db_user)
        db.commit()
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Delete failed: {e.orig}") from e
