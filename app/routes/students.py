from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database.db import get_all_students

router = APIRouter

templates = Jinja2Templates(directory='templates')

@router.get('/students')
def students_page(request: Request):
    students = get_all_students()
    return templates.TemplateResponse(
        'students/list.html',
        {'request': request, 'students': students}
    )