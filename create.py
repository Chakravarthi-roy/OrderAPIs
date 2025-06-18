from sqlalchemy.orm import Session, joinedload
from db.tables import Order, OrderItem, Product, User
from schemas import OrderCreate, ProductCreate, UserBase
from hash import Hash
from datetime import datetime
from decimal import Decimal

def createProduct(db: Session, product_data: ProductCreate):
    existing_product = db.query(Product).filter(Product.product_name == product_data.product_name).first()
    if existing_product:
        raise ValueError(f"Product with name '{product_data.product_name}' already exists.")
    
    db_product = Product(
        product_name = product_data.product_name,
        price = product_data.price,
        time_req = product_data.time_req,
        category = product_data.category,
        description = product_data.description
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def createOrder(db: Session, order_data: OrderCreate):
    db_order = Order(
        user_id = order_data.user_id,
        order_time = datetime.utcnow(),
        prep_status = "pending",
        delivery_status = "pending",
        total_amount = Decimal('0.00')
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    calculated_total = Decimal('0.00')
    db_order_items = []

    for item_data in order_data.items:
        product = db.query(Product).filter(Product.product_name == item_data.product_name).first()
        if not product:
            db.rollback()
            raise ValueError(f"Product '{item_data.product_name}' not found.")

        item_price_at_order = product.price
        calculated_total += item_price_at_order * item_data.quantity

        db_order_item = OrderItem(
            order_id = db_order.order_id,
            product_name = item_data.product_name,
            quantity = item_data.quantity,
            item_price_at_order = item_price_at_order
        )
        db_order_items.append(db_order_item)
    
    db.add_all(db_order_items)
    db_order.total_amount = calculated_total
    
    db.commit()
    db.refresh(db_order)
    db_order = db.query(Order).options(joinedload(Order.order_items)).filter(Order.order_id == db_order.order_id).first()
    return db_order

def create_user(db: Session, request = UserBase):
    new_user = User(
        email = request.email,
        hashed_password = Hash.bcrypt(request.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
