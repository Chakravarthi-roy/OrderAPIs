from sqlalchemy import Boolean, Column, DateTime, Integer, String, Time, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    address = Column(String)

    orders = relationship("Order", backref="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"


class Product(Base):
    __tablename__ = "products"

    product_name = Column(String, primary_key=True)
    price = Column(Numeric(10, 2), nullable=False)
    price = Column(Integer)
    time_req = Column(Integer)
    category = Column(String)
    description = Column(String)

    order_items = relationship("OrderItem", backref="product")

    def __repr__(self):
        return f"<Product(name='{self.product_name}', price={self.price})>"


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_time = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Numeric(10, 2))
    prep_status = Column(String, default="pending")
    delivery_status = Column(String, default="pending")

    order_items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.order_id}, user_id={self.user_id}, status='{self.delivery_status}')>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    product_name = Column(String, ForeignKey('products.product_name'), nullable=False)
    quantity = Column(Integer, nullable=False)
    item_price_at_order = Column(Numeric(10, 2), nullable=False)

    def __repr__(self):
        return (f"<OrderItem(id={self.id}, order_id={self.order_id}, "
                f"product_name='{self.product_name}', quantity={self.quantity})>")

class Item(Base):
    __tablename__ = "items"

    item_name = Column(String, ForeignKey('products.product_name'))
    quantity = Column(Integer)
    customer_name = Column(String, primary_key=True)
    order_time = Column(Time("HH:MM:SS"))
    prep_status = Column(Boolean, default=False)
    delivery_status = Column(Boolean, default=False)
