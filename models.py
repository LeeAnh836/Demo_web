from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, TEXT, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# Mô hình ORM cho bảng `user`
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    account = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(15))
    address = Column(String(255))

# Mô hình ORM cho bảng `product`
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    description = Column(TEXT)
    price = Column(DECIMAL(10,2))
    stock = Column(Integer)

# Mô hình ORM cho bảng `order`
class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    price_1 = Column(DECIMAL(10,2))
    order_date = Column(Date)
    status = Column(String(50))
    quantity = Column(Integer)
    total_amount = Column(DECIMAL(10,2))
    
    user = relationship('User', back_populates="orders")
    product = relationship('Product', back_populates="orders")

User.orders = relationship('Order', back_populates="user")
Product.orders = relationship('Order', back_populates="product")