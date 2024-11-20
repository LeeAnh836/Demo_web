from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import User
from sqlalchemy import create_engine
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

# Schema để nhận dữ liệu từ yêu cầu POST
class UserCreate(BaseModel):
    name: str
    account: str
    password: str
    email: EmailStr
    phone: str
    address: str

# Hàm để lấy một phiên làm việc (session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# API lấy thông tin người dùng
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# API thêm một người dùng mới
@router.post("/users")
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra nếu tài khoản đã tồn tại
    existing_user = db.query(User).filter(User.account == user_create.account).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Account already registered")
    
    # Tạo đối tượng User mới từ dữ liệu nhận được
    new_user = User(
        name=user_create.name,
        account=user_create.account,
        password=user_create.password,
        email=user_create.email,
        phone=user_create.phone,
        address=user_create.address
    )
    
    # Lưu người dùng vào cơ sở dữ liệu
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# API GET: Tìm kiếm người dùng thông qua ID
@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    # Tìm kiếm người dùng theo ID
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user