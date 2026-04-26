from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database.db import get_connection

router = APIRouter()
templates = Jinja2Templates(directory='templates')

def _rows_to_dicts(rows):
    return [dict(row) for row in rows] if rows else []

@router.get('/students')
def students_page(request: Request):
    conn = get_connection()
    students = _rows_to_dicts(conn.execute('SELECT * FROM students').fetchall())
    conn.close()
    return templates.TemplateResponse(request, 'students/list.html', {'students': students})

@router.get('/students/add')
def add_student_form(request: Request):
    return templates.TemplateResponse(request, 'students/add.html')

@router.post('/students/add')
def add_student(
    request: Request,
    name: str = Form(...),
    class_name: str = Form(...),
    coins: int = Form(0),
    data: str = Form(""),
    login: str = Form(...),
    password: str = Form(""),
):
    conn = get_connection()
    conn.execute(
        'INSERT INTO students (name, coins, class, data, login, password) VALUES (?, ?, ?, ?, ?, ?)',
        (name, coins, class_name, data, login, password or "")
    )
    conn.commit()
    conn.close()
    return RedirectResponse('/students', status_code=303)

# ---------- УДАЛЕНИЕ ----------
@router.post('/students/delete/{student_id}')
def delete_student(request: Request, student_id: int):
    conn = get_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return RedirectResponse('/students', status_code=303)

# ---------- РЕДАКТИРОВАНИЕ (форма) ----------
@router.get('/students/edit/{student_id}')
def edit_student_form(request: Request, student_id: int):
    conn = get_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return templates.TemplateResponse(request, 'students/edit.html', {'student': dict(student)})

# ---------- РЕДАКТИРОВАНИЕ (сохранение) ----------
@router.post('/students/edit/{student_id}')
def edit_student(
    request: Request,
    student_id: int,
    name: str = Form(...),
    class_name: str = Form(...),
    coins: int = Form(0),
    data: str = Form(""),
    login: str = Form(""),
    password: str = Form(""),
):
    conn = get_connection()
    conn.execute(
        'UPDATE students SET name = ?, class = ?, coins = ?, data = ?, login = ?, password = ? WHERE id = ?',
        (name, class_name, coins, data, login, password or "", student_id)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url='/students', status_code=303)