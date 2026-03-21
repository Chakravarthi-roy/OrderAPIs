from sqlalchemy.orm import Session, joinedload
from db.tables import Order, OrderItem, Product, User
from db.schemas import OrderCreate, ProductCreate, UserCreate, PrepStatus, DeliveryStatus
from db.hash import Hash
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

def createProduct(db: Session, product_data: ProductCreate):
    existing_product = db.query(Product).filter(Product.product_name == product_data.product_name).first()
    if existing_product:
        raise ValueError(f"Product '{product_data.product_name}' already exists")
    try:
        db_product = Product(
            product_name=product_data.product_name,
            price=product_data.price,
            time_req=product_data.time_req,
            category=product_data.category,
            description=product_data.description
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e)}")

def createOrder(db: Session, order_data: OrderCreate):
    user = db.query(User).filter(User.id == order_data.user_id).first()
    if not user:
        raise ValueError(f"User ID {order_data.user_id} not found")
    if not order_data.items:
        raise ValueError("Order must contain at least one item")
    try:
        db_order = Order(
            user_id=order_data.user_id,
            prep_status=PrepStatus.PENDING,
            delivery_status=DeliveryStatus.PENDING,
            total_amount=Decimal('0.00')
        )
        db.add(db_order)
        db.flush()  # Get ID before adding items
        total = Decimal('0.00')
        order_items = []
        for item_data in order_data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise ValueError(f"Product ID {item_data.product_id} not found")
            price_at_order = product.price
            total += price_at_order * item_data.quantity
            order_items.append(OrderItem(
                order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price_at_order=price_at_order
            ))
        db.bulk_save_objects(order_items)
        db_order.total_amount = total
        db.commit()
        db.refresh(db_order)
        return db.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.order_items).joinedload(OrderItem.product_related)
        ).filter(Order.id == db_order.id).first()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Order creation failed: {str(e)}")

def createUser(db: Session, user_data: UserCreate):
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        if existing_user.username == user_data.username:
            raise ValueError('Username already exists')
        raise ValueError('Email already registered')
    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=Hash.bcrypt(user_data.password),
            full_name=user_data.full_name,
            hostel_no=user_data.hostel_no
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"User creation failed: {str(e)}")