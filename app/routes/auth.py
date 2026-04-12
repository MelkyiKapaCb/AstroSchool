import sqlite3

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.security import verify_password
from app.templates_shared import templates
from database.db import get_user_by_email, register_user_with_student

router = APIRouter()


@router.get("/login")
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "auth/login.html", {})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_email(email)
    if user is None or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Неверный email или пароль"},
        )
    request.session["user_id"] = user["id"]
    return RedirectResponse("/", status_code=303)


@router.get("/register")
def register_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "auth/register.html", {})


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(...),
):
    try:
        register_user_with_student(email, password, display_name)
    except sqlite3.IntegrityError:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {"error": "Не удалось зарегистрироваться. Возможно, email уже занят."},
        )
    user = get_user_by_email(email)
    if user:
        request.session["user_id"] = user["id"]
    return RedirectResponse("/profile", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
