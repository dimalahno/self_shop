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

# Создание товара
@router.post("/", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        image_url=str(product.image_url)
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Получение всех товаров
@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(db: Session = Depends(get_db)):
    db_products = db.query(models.Product).all()
    return db_products

# Получение товара по ID
@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Обновление товара
@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.category_id = product.category_id
    db_product.image_url = str(product.image_url)
    db.commit()
    db.refresh(db_product)
    return db_product

# Удаление товара
@router.delete("/{product_id}", response_model=schemas.ProductResponse)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return db_product
