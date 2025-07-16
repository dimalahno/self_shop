from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter()

# Инициализация Jinja2
templates = Jinja2Templates(directory="app/templates")

# Главная страница (каталог товаров)
@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(database.get_db)):
    db_products = db.query(models.Product).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": db_products})

# Страница каталога товаров
@router.get("/catalog", response_class=HTMLResponse)
async def read_catalog(request: Request, db: Session = Depends(database.get_db)):
    db_products = db.query(models.Product).all()
    return templates.TemplateResponse("catalog.html", {"request": request, "products": db_products})

# Страница корзины
@router.get("/cart", response_class=HTMLResponse)
async def read_cart(request: Request):
    # Для простоты корзина будет представлена в виде сессионных данных
    cart = request.cookies.get("cart", "")
    return templates.TemplateResponse("cart.html", {"request": request, "cart": cart})

# Добавление товара в корзину
@router.post("/cart/add/{product_id}")
async def add_to_cart(product_id: int, request: Request):
    # Для простоты будем хранить корзину в cookies
    cart = request.cookies.get("cart", "")
    cart = cart.split(",") if cart else []
    
    if str(product_id) not in cart:
        cart.append(str(product_id))  # Добавляем товар в корзину
    
    # Обновляем cookies с новой корзиной
    response = JSONResponse(content={"message": "Product added to cart"})
    response.set_cookie(key="cart", value=",".join(cart))
    return response