from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# HTML-форма регистрации
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user_form(request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
    db_email = db.query(models.User).filter(models.User.email == email).first()
    if db_email:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email уже зарегистрирован"})
    hashed_password = auth.hash_password(password)
    db_user = models.User(username=username, email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RedirectResponse(url="/", status_code=303)

# HTML-форма логина
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_user_form(request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None or not auth.verify_password(password, db_user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные учетные данные"})
    access_token = auth.create_access_token(data={"sub": db_user.id, "role": db_user.role})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# JWT-зависимость
SECRET_KEY = "SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        role = payload.get("role", "user")
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# HTML-админка (только для админа)
@router.get("/admin-panel", response_class=HTMLResponse)
async def admin_panel(request: Request, current_user: models.User = Depends(admin_required)):
    return templates.TemplateResponse("admin_panel.html", {"request": request, "user": current_user})