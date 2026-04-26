# app/routes/student.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from database.db import get_student_by_id, get_transactions_by_student

router = APIRouter(prefix="/student", tags=["student"])
templates = Jinja2Templates(directory="templates")
student_id = 1
@router.get("/{student_id}")
async def student_profile(request: Request, student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Преобразуем row в dict
    student_dict = dict(student)
    student_dict["transactions"] = get_transactions_by_student(student_id)
    
    return templates.TemplateResponse("student_list/student_profile.html", {
        "request": request,
        "student": student_dict
    })