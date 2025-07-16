from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database

router = APIRouter()

# Получаем сессию базы данных
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Только администратор
def admin_required(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

# Добавление товара
@router.post("/products", response_model=schemas.ProductResponse)
async def add_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Обновление товара
@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
async def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.category_id = product.category_id
    db.commit()
    db.refresh(db_product)
    return db_product

# Удаление товара
@router.delete("/products/{product_id}", response_model=schemas.ProductResponse)
async def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return db_product

# Просмотр всех заказов
@router.get("/orders", response_model=List[schemas.OrderResponse])
async def get_orders(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_orders = db.query(models.Order).all()
    return db_orders

# Обновление статуса заказа
@router.put("/orders/{order_id}", response_model=schemas.OrderResponse)
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order

# Просмотр всех пользователей
@router.get("/users", response_model=List[schemas.UserResponse])
async def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_users = db.query(models.User).all()
    return db_users

# Блокировка пользователя
@router.put("/users/{user_id}/block", response_model=schemas.UserResponse)
async def block_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False  # Блокируем пользователя
    db.commit()
    db.refresh(db_user)
    return db_user

# Удаление пользователя
@router.delete("/users/{user_id}", response_model=schemas.UserResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return db_user
