from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy các thông tin từ môi trường
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Chuỗi kết nối MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo engine cho SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model cho các lớp ORM
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
class UserCreate(BaseModel):
    name: str
    account: str
    password: str
    email: EmailStr
    phone: str
    address: str

# API GET: Lấy danh sách tất cả người dùng
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# API POST: Thêm người dùng mới
@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem tài khoản hoặc email đã tồn tại chưa
    if db.query(User).filter((User.account == user.account) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Account or email already exists")

    # Tạo đối tượng User từ dữ liệu yêu cầu
    new_user = User(
        name=user.name,
        account=user.account,
        password=user.password,  # Lưu ý: Nên mã hóa mật khẩu trước khi lưu
        email=user.email,
        phone=user.phone,
        address=user.address 
    )

    # Thêm người dùng mới vào cơ sở dữ liệu
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# API GET: Tìm kiếm người dùng thông qua ID
@app.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    # Tìm kiếm người dùng theo ID
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user