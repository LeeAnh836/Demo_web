from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User, Product, Order
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine, DECIMAL, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo engine cho SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    price_1: Decimal
    order_date: date  
    status: str
    quantity: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True  # Cho phép kiểu dữ liệu tùy chỉnh

class OrderOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    price_1: Decimal
    order_date: date  # Dùng kiểu `date` chuẩn của Python thay vì `sqlalchemy.Date`
    status: str
    quantity: int
    total_amount: Decimal

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True  # Cho phép kiểu dữ liệu tùy chỉnh



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API lấy thông tin đơn hàng
@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders


# API tạo đơn hàng
@router.post("/orders", response_model=OrderOut)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Truy vấn sản phẩm từ cơ sở dữ liệu theo product_id
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Kiểm tra số lượng tồn kho
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    # Tính toán tổng tiền
    total_amount = order.price_1 * order.quantity

    # Tạo đơn hàng
    new_order = Order(
        user_id=order.user_id,
        product_id=order.product_id,
        price_1=product.price,  # Sử dụng giá của sản phẩm trong cơ sở dữ liệu
        order_date=order.order_date,
        status=order.status,
        quantity=order.quantity,
        total_amount=total_amount
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return OrderOut.from_orm(new_order)
