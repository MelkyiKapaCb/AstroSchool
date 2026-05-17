from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from database.db import (
    verify_user,
    create_user,
    get_all_users,
    delete_user,
    get_all_teachers,
    create_teacher,
    delete_teachers,
    get_connection,
)
from functools import wraps

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Декоратор для проверки роли
def login_required(role=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = request.session.get("user")
            if not user:
                raise HTTPException(status_code=303, headers={"Location": "/login"})
            if role and user.get("role") != role:
                return HTMLResponse("Доступ запрещён", status_code=403)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Страница входа
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = verify_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
        )
    
    request.session["user"] = user
    
    # Перенаправляем в зависимости от роли
    if user["role"] == "admin":
        return RedirectResponse("/admin", status_code=303)
    elif user["role"] == "teacher":
        return RedirectResponse("/teacher/students", status_code=303)
    else:
        return RedirectResponse("/students", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# Админ-панель
@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)
    
    teachers = get_all_teachers()
    users = get_all_users()
    
    return templates.TemplateResponse(
        "admin/panel.html",
        {"request": request, "teachers": teachers, "users": users},
    )


@router.post("/admin/create-teacher")
async def create_teacher_account(
    request: Request,
    teacher_name: str = Form(...),
    class_name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)
    
    # Создаём учителя в таблице teachers
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO teachers (name, class) VALUES (?, ?)",
        (teacher_name, class_name),
    )
    teacher_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Создаём пользователя для учителя
    create_user(username, password, "teacher", teacher_id=teacher_id)
    
    return RedirectResponse("/admin", status_code=303)


@router.delete("/admin/delete-teacher/{teacher_id}")
async def delete_teacher_account(teacher_id: int, request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse({"error": "Доступ запрещён"}, status_code=403)
    
    # Удаляем пользователя связанного с учителем
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE teacher_id = ?", (teacher_id,))
    conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()
    
    return JSONResponse({"message": "OK"})


@router.delete("/admin/delete-user/{user_id}")
async def delete_user_account(user_id: int, request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return JSONResponse({"error": "Доступ запрещён"}, status_code=403)
    
    delete_user(user_id)
    return JSONResponse({"message": "OK"})


# Учитель видит своих учеников
@router.get("/teacher/students", response_class=HTMLResponse)
async def teacher_students(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "teacher":
        return RedirectResponse("/login", status_code=303)
    
    teacher_id = user.get("teacher_id")
    teacher = get_connection().execute(
        "SELECT * FROM teachers WHERE id = ?", (teacher_id,)
    ).fetchone()
    
    if not teacher:
        return HTMLResponse("Учитель не найден", status_code=404)
    
    students = get_connection().execute(
        "SELECT * FROM students WHERE class = ?", (teacher["class"],)
    ).fetchall()
    
    return templates.TemplateResponse(
        "teacher/students.html",
        {"request": request, "teacher": teacher, "students": students},
    )


# Учитель добавляет ученика
@router.post("/teacher/add-student")
async def teacher_add_student(
    request: Request,
    name: str = Form(...),
    coins: int = Form(0),
    data: str = Form(""),
):
    user = request.session.get("user")
    if not user or user.get("role") != "teacher":
        return RedirectResponse("/login", status_code=303)
    
    teacher_id = user.get("teacher_id")
    teacher = get_connection().execute(
        "SELECT * FROM teachers WHERE id = ?", (teacher_id,)
    ).fetchone()
    
    if teacher:
        conn = get_connection()
        conn.execute(
            "INSERT INTO students (name, coins, class, data) VALUES (?, ?, ?, ?)",
            (name, coins, teacher["class"], data),
        )
        conn.commit()
        conn.close()
    
    return RedirectResponse("/teacher/students", status_code=303)