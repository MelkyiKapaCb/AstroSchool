from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.templates_shared import templates
from database.db import get_student_by_user_id

router = APIRouter()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "pages/home.html", {})


@router.get("/profile")
def profile(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=303)
    student = get_student_by_user_id(int(uid))
    return templates.TemplateResponse(
        request,
        "pages/profile.html",
        {"student": student},
    )
