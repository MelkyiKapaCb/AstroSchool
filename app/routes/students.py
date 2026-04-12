from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.templates_shared import templates
from database.db import create_student, get_all_students, get_student, get_user_by_id

router = APIRouter()


def _admin_ok(request: Request) -> bool:
    uid = request.session.get("user_id")
    if not uid:
        return False
    u = get_user_by_id(int(uid))
    return u is not None and bool(u["is_admin"])


@router.get("/students")
def students_page(request: Request):
    students = get_all_students()
    return templates.TemplateResponse(
        request,
        "students/list.html",
        {"students": students},
    )


@router.get("/students/add")
def students_add_form(request: Request):
    if not _admin_ok(request):
        return RedirectResponse("/students", status_code=303)
    return templates.TemplateResponse(request, "form/student_form.html", {})


@router.get("/students/{student_id:int}")
def student_detail(request: Request, student_id: int):
    student = get_student(student_id)
    if student is None:
        return RedirectResponse("/students", status_code=303)
    return templates.TemplateResponse(
        request,
        "students/detail.html",
        {"student": student},
    )


@router.post("/students/add")
def add_student(
    request: Request,
    name: str = Form(...),
    class_name: str = Form(...),
):
    if not _admin_ok(request):
        return RedirectResponse("/students", status_code=303)
    create_student(name, class_name)
    return RedirectResponse("/students", status_code=303)
