from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter()

# Получаем сессию базы данных как зависимость
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создание заказа
@router.post("/", response_model=schemas.OrderResponse)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(user_id=order.user_id, total_price=0)  # Сначала создаём заказ без товаров
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Добавляем товары в заказ
    total_price = 0
    for product_id in order.product_ids:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
        order_item = models.OrderItem(order_id=db_order.id, product_id=product.id, quantity=1)
        db.add(order_item)
        total_price += product.price
    db.commit()

    db_order.total_price = total_price
    db.commit()

    return db_order

# Получение всех заказов
@router.get("/", response_model=List[schemas.OrderResponse])
async def read_orders(db: Session = Depends(get_db)):
    db_orders = db.query(models.Order).all()
    return db_orders

# Получение заказа по ID
@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Удаление заказа
@router.delete("/{order_id}", response_model=schemas.OrderResponse)
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(db_order)
    db.commit()
    return db_order
