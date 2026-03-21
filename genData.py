from faker import Faker
from sqlalchemy.orm import Session
from decimal import Decimal
import random

from db.tables import User, Product, Order, OrderItem
from database import SessionLocal

fake = Faker()
db: Session = SessionLocal()

# --- Fetch existing user and product IDs ---
user_ids = [u.id for u in db.query(User.id).all()]
product_ids = [p.id for p in db.query(Product.id).all()]

if not user_ids or not product_ids:
    print("No users or products found. Please seed users and products first!")
    db.close()
    exit()

# --- Seed Orders and OrderItems ---
num_orders = 200

for _ in range(num_orders):
    user_id = random.choice(user_ids)
    order = Order(
        user_id=user_id,
        prep_status="pending",
        delivery_status="pending",
        total_amount=Decimal('0.00')
    )
    db.add(order)
    db.flush()  # To get order.id before adding items

    order_total = Decimal('0.00')
    num_items = random.randint(1, 5)
    chosen_product_ids = random.sample(product_ids, min(num_items, len(product_ids)))

    for product_id in chosen_product_ids:
        product = db.query(Product).filter(Product.id == product_id).first()
        quantity = random.randint(1, 3)
        price_at_order = product.price
        item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            price_at_order=price_at_order
        )
        db.add(item)
        order_total += price_at_order * quantity

    order.total_amount = order_total
    db.flush()

# --- Commit all changes ---
try:
    db.commit()
    print("Orders and order items seeded successfully.")
except Exception as e:
    db.rollback()
    print(f"Error seeding orders: {e}")
finally:
    db.close()