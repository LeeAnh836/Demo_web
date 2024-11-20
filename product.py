from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, TEXT
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

# Base model cho các lớp ORM
Base = declarative_base()

# Mô hình ORM cho bảng `product`
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    description = Column(TEXT)
    price = Column(DECIMAL(10,2))
    stock = Column(Integer)

# Tạo ứng dụng FastAPI
app = FastAPI()

# Dependency: Kết nối với cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schema để nhận dữ liệu từ yêu cầu POST
class ProductCreate(BaseModel):
    name: str
    description: str
    price: DECIMAL
    stock: int
    class Config:
        arbitrary_types_allowed = True

# API GET: Lấy danh sách tất cả sản phẩm
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# API POST: Thêm sản phẩm mới mới
@app.post("/products", status_code=201)
def create_products(product: ProductCreate, db: Session = Depends(get_db)):

    # Tạo đối tượng Product từ dữ liệu yêu cầu
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock 
    )

    # Thêm sản phẩm mới vào cơ sở dữ liệu
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

# API GET: Tìm kiếm sản phẩm thông qua ID
@app.get("/products/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    # Tìm kiếm sản phẩm theo ID
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="User not found")

    return product