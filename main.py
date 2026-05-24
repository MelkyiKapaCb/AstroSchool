from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from database.db import init_db
from app.routes.students import router as students_router
from app.routes.student import router as student_router
from app.routes.shop import router as shop_router
from app.routes.cart import router as cart_router
from app.balance import router as balance_router
from app.auth import router as auth_router

app = FastAPI()

# Добавляем поддержку сессий (ОБЯЗАТЕЛЬНО!)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(student_router)
app.include_router(shop_router)
app.include_router(cart_router)
app.include_router(balance_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if user["role"] == "admin":
        return RedirectResponse("/admin", status_code=303)
    elif user["role"] == "teacher":
        return RedirectResponse("/teacher/students", status_code=303)
    elif user["role"] == "student" and user.get("student_id"):
        return RedirectResponse(f"/student/{user['student_id']}", status_code=303)
    return RedirectResponse("/login", status_code=303)