from fastapi import FastAPI
from user import router as user_router  # Import router từ user.py
from product import router as product_router # Import router từ product.py
from order import router as order_router # Import router từ order.py

app = FastAPI()

# Thêm router vào ứng dụng chính
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
