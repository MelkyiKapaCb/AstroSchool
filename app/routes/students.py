from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database.db import create_student, get_all_students, get_connection  # добавьте get_connection

router = APIRouter()
templates = Jinja2Templates(directory='templates')

def _rows_to_dicts(rows):
    """Конвертирует sqlite3.Row в список dict для безопасного доступа в Jinja2."""
    return [dict(row) for row in rows] if rows else []

@router.get('/students')
def students_page(request: Request):
    students = _rows_to_dicts(get_all_students())  # ✅ Конвертация
    return templates.TemplateResponse(request, 'students/list.html', {'students': students})

@router.get('/students/add')
def add_student_form(request: Request):
    return templates.TemplateResponse(request, 'students/add.html')

@router.post('/students/add')
async def add_student(
    request: Request,  # ✅ Обязательно для TemplateResponse
    name: str = Form(...),
    class_name: str = Form(...),  # name атрибута в форме
    coins: int = Form(0),          # ✅ Новые поля
    data: str = Form("")
):
    # ✅ Используем полную функцию добавления
    conn = get_connection()
    conn.execute(
        'INSERT INTO students (name, coins, class, data) VALUES (?, ?, ?, ?)',
        (name, coins, class_name, data)
    )
    conn.commit()
    conn.close()
    return RedirectResponse('/students', status_code=303)






