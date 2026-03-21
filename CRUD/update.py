from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from db.schemas import OrderUpdate, ProductUpdate, UserUpdate, PrepStatus, DeliveryStatus
from db.tables import Order, OrderItem, Product, User

def updateProduct(db: Session, product_id: int, request: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise ValueError("Product not found")
    update_data = request.model_dump(exclude_unset=True)
    if 'product_name' in update_data and update_data['product_name'] != db_product.product_name:
        if db.query(Product).filter(Product.product_name == update_data['product_name']).first():
            raise ValueError("Product name already in use")
    for key, value in update_data.items():
        setattr(db_product, key, value)
    try:
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Update failed: {str(e)}")

def updateOrder(db: Session, order_id: int, order_update: OrderUpdate):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise ValueError("Order not found")
    update_data = order_update.model_dump(exclude_unset=True)
    if 'prep_status' in update_data:
        try:
            PrepStatus(update_data['prep_status'])
        except ValueError:
            raise ValueError("Invalid prep_status value")
    if 'delivery_status' in update_data:
        try:
            DeliveryStatus(update_data['delivery_status'])
        except ValueError:
            raise ValueError("Invalid delivery_status value")
    for key, value in update_data.items():
        setattr(db_order, key, value)
    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Update failed: {str(e)}")

def updateOrderItem(db: Session, order_id: int, item_id: int, new_quantity: int):
    if new_quantity <= 0:
        raise ValueError("Quantity must be positive")
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise ValueError(f"Order with ID {order_id} not found.")
    db_item = db.query(OrderItem).filter(OrderItem.id == item_id, OrderItem.order_id == order_id).first()
    if not db_item:
        raise ValueError("Order item not found.")
    old_total_contribution = db_item.quantity * db_item.price_at_order
    db_item.quantity = new_quantity
    new_total_contribution = db_item.quantity * db_item.price_at_order
    db_order.total_amount = db_order.total_amount - old_total_contribution + new_total_contribution
    try:
        db.commit()
        db.refresh(db_item)
        db.refresh(db_order)
        return db_item
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Update failed: {str(e)}")

def updateUser(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise ValueError("User not found")
    update_data = user_update.model_dump(exclude_unset=True)
    if 'username' in update_data and update_data['username'] != db_user.username:
        if db.query(User).filter(User.username == update_data['username']).first():
            raise ValueError("Username already taken")
    if 'email' in update_data and update_data['email'] != db_user.email:
        if db.query(User).filter(User.email == update_data['email']).first():
            raise ValueError("Email already registered")
    for key, value in update_data.items():
        setattr(db_user, key, value)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Update failed: {str(e)}")
