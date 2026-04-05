from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database.db import create_student, get_all_students

router = APIRouter

templates = Jinja2Templates(directory='templates')

@router.get('/students')
def students_page(request: Request):
    students = get_all_students()
    return templates.TemplateResponse(
        'students/list.html',
        {'request': request, 'students': students}
    )

@router.get('/students')
def list_students():
    students = get_all_students
    return [dict (s) for s in students]

#app/routes/students.py
from fastapi import Form
from fastapi.responses import RedirectResponse

@router.post('/students/add')
def add_student(name: str = Form(...), class_name: str = Form(...)):
    create_student(name, class_name)
    return RedirectResponse('/students', status_code=303)