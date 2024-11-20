from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Product
from decimal import Decimal
from sqlalchemy import create_engine, DECIMAL, Integer, String
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

class ProductCreate(BaseModel):
    name: str
    description: str
    price: Decimal  # Sử dụng Decimal từ thư viện decimal
    stock: int  # Integer không cần phải khai báo kiểu SQLAlchemy tại đây

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int

    class Config:
        orm_mode = True  # Đảm bảo chuyển đổi từ ORM model sang schema Pydantic

# Hàm để lấy một phiên làm việc (session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# API lấy thông tin sản phẩm
@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# API thêm một sản phẩm mới
@router.post("/products", response_model=ProductOut)
def create_product(product_create: ProductCreate, db: Session = Depends(get_db)):
    # Kiểm tra nếu sản phẩm đã tồn tại
    existing_product = db.query(Product).filter(Product.name == product_create.name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product already exists")
    
    # Tạo đối tượng Product mới từ dữ liệu nhận được
    new_product = Product(
        name=product_create.name,
        description=product_create.description,
        price=product_create.price,
        stock=product_create.stock
    )
    
    # Lưu sản phẩm vào cơ sở dữ liệu
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return ProductOut.from_orm(new_product)

# API GET: Tìm kiếm sản phẩm thông qua ID
@router.get("/products/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    # Tìm kiếm sản phẩm theo ID
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product