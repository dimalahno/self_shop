# Схема для товара
from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    image_url: HttpUrl

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Название не может быть пустым')
        return v

    @field_validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть больше 0')
        return v


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    image_url: HttpUrl

    class Config:
        orm_mode = True

# Схема для категории
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Схема для пользователя
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

# Схема для заказа
class OrderCreate(BaseModel):
    user_id: int
    product_ids: List[int]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_ids: List[int]
    total_price: float

    class Config:
        orm_mode = True