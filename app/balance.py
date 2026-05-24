from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from database.db import get_connection, add_coins, delete_coins, get_student_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/teacher/balance/{student_id}", response_class=HTMLResponse)
async def manage_balance_form(request: Request, student_id: int):
    user = request.session.get("user")
    if not user or user.get("role") not in ["teacher", "admin"]:
        return RedirectResponse("/login", status_code=303)
    
    student = get_student_by_id(student_id)
    if not student:
        return RedirectResponse("/teacher/students", status_code=303)
    
    return templates.TemplateResponse(
        "teacher/manage_balance.html",
        {
            "request": request,
            "student": dict(student),
            "student_id": student_id
        }
    )

@router.post("/teacher/add-coins")
async def add_coins_to_student(
    request: Request,
    student_id: int = Form(...),
    amount: int = Form(...)
):
    user = request.session.get("user")
    if not user or user.get("role") not in ["teacher", "admin"]:
        return RedirectResponse("/login", status_code=303)
    
    if amount > 0:
        add_coins(student_id, amount)
        
        # Записываем транзакцию
        conn = get_connection()
        conn.execute(
            "INSERT INTO transactions (student_id, amount, reason) VALUES (?, ?, ?)",
            (student_id, amount, f"Начислено учителем {user.get('username')}")
        )
        conn.commit()
        conn.close()
    
    return RedirectResponse(f"/teacher/students", status_code=303)

@router.post("/teacher/remove-coins")
async def remove_coins_from_student(
    request: Request,
    student_id: int = Form(...),
    amount: int = Form(...)
):
    user = request.session.get("user")
    if not user or user.get("role") not in ["teacher", "admin"]:
        return RedirectResponse("/login", status_code=303)
    
    student = get_student_by_id(student_id)
    
    if amount > 0 and student and student["coins"] >= amount:
        delete_coins(student_id, amount)
        
        # Записываем транзакцию
        conn = get_connection()
        conn.execute(
            "INSERT INTO transactions (student_id, amount, reason) VALUES (?, ?, ?)",
            (student_id, -amount, f"Списано учителем {user.get('username')}")
        )
        conn.commit()
        conn.close()
    
    return RedirectResponse(f"/teacher/students", status_code=303)