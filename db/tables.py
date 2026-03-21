from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100))
    hostel_no = Column(Integer)
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username!r})>"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), unique=True, index=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    time_req = Column(Integer)
    category = Column(String(50))
    description = Column(String(255))
    # Removed cascade here — deleting a product should NOT wipe historical order items
    order_items_related = relationship("OrderItem", back_populates="product_related")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.product_name!r}, price={self.price})>"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    order_time = Column(DateTime(timezone=True), server_default=func.now())
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    prep_status = Column(String(20), default="pending")
    delivery_status = Column(String(20), default="pending")
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.delivery_status!r})>"

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Numeric(10, 2), nullable=False)
    order = relationship("Order", back_populates="order_items")
    product_related = relationship("Product", back_populates="order_items_related")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"