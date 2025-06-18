from sqlalchemy.orm.session import Session
from db.tables import Order, OrderItem, Product

def deleteProduct(db: Session, p_name: str):
    db_product = db.query(Product).filter(Product.product_name == p_name).first()
    if not db_product:
        return None

    db.delete(db_product)
    db.commit()
    return db_product

def deleteOrder(db: Session, order_id: int):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if not db_order:
        return None
    db.delete(db_order)
    db.commit()
    return db_order

def deleteOrderItem(db: Session, order_id: int, item_id: int):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if not db_order:
        raise ValueError(f"Order with ID {order_id} not found.")

    db_item = db.query(OrderItem).filter(OrderItem.id == item_id, OrderItem.order_id == order_id).first()
    if not db_item:
        return None
    
    db_order.total_amount -= (db_item.quantity * db_item.item_price_at_order)

    db.delete(db_item)
    db.commit()
    db.refresh(db_order)
    return db_item