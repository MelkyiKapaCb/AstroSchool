# from fastapi import APIRouter, Request, Form
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import RedirectResponse
# from database.db import create_student, get_all_students

# router = APIRouter()
# templates = Jinja2Templates(directory='templates')

# @router.get('/students')
# def students_page(request: Request):
#     students = get_all_students()
#     return templates.TemplateResponse('students/list.html', {'request': request, 'students': students})

# @router.get('/students/add')
# def add_student_form(request: Request):
#     return templates.TemplateResponse('students/add.html', {'request': request})

# @router.post('/students/add')
# def add_student(name: str = Form(...), class_name: str = Form(...)):
#     create_student(name, class_name)
#     return RedirectResponse('/students', status_code=303)

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import create_student, get_all_students

router = APIRouter()

@router.get('/students')
def students_page(request: Request):
    # Простой HTML, чтобы проверить, работает ли маршрут
    html = """
    <h1>Тест</h1>
    <p>Если вы видите этот текст, значит FastAPI работает.</p>
    <a href="/students/add">Добавить студента</a>
    """
    return HTMLResponse(content=html)

@router.get('/students/add')
def add_student_form(request: Request):
    # Простая форма
    html_form = """
    <h2>Добавить студента</h2>
    <form method="post" action="/students/add">
        <label>Имя: <input type="text" name="name"></label><br>
        <label>Класс: <input type="text" name="class_name"></label><br>
        <button type="submit">Сохранить</button>
    </form>
    <a href="/students">Назад</a>
    """
    return HTMLResponse(content=html_form)

@router.post('/students/add')
def add_student(name: str = Form(...), class_name: str = Form(...)):
    create_student(name, class_name)
    return RedirectResponse('/students', status_code=303)