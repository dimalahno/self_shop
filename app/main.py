# main.py
from fastapi import FastAPI
from .database import Base, engine
from .models import User, Product
# Если есть ваши роуты
from .routes import admin, auth, frontend, orders, products

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Создаём приложение
app = FastAPI()

# Подключаем свои роуты
app.include_router(admin.router, prefix="/admin-panel", tags=["admin-panel"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(frontend.router, tags=["frontend"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(products.router, prefix="/products", tags=["products"])
