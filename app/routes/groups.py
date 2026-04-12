from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.templates_shared import templates
from database.db import (
    add_student_to_group,
    create_group,
    get_all_groups,
    get_all_students,
    get_group,
    get_student_ids_in_group,
    get_students_in_group,
    get_user_by_id,
    remove_student_from_group,
)

router = APIRouter()


def _admin_ok(request: Request) -> bool:
    uid = request.session.get("user_id")
    if not uid:
        return False
    u = get_user_by_id(int(uid))
    return u is not None and bool(u["is_admin"])


@router.get("/groups")
def groups_list(request: Request):
    groups = get_all_groups()
    return templates.TemplateResponse(
        request,
        "groups/list.html",
        {"groups": groups},
    )


@router.post("/groups/add")
def groups_add(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
):
    if not _admin_ok(request):
        return RedirectResponse("/groups", status_code=303)
    create_group(name, description)
    return RedirectResponse("/groups", status_code=303)


@router.get("/groups/{group_id:int}")
def group_detail(request: Request, group_id: int):
    group = get_group(group_id)
    if group is None:
        return RedirectResponse("/groups", status_code=303)
    members = get_students_in_group(group_id)
    member_ids = get_student_ids_in_group(group_id)
    all_students = get_all_students()
    available = [s for s in all_students if s["id"] not in member_ids]
    return templates.TemplateResponse(
        request,
        "groups/detail.html",
        {
            "group": group,
            "members": members,
            "available_students": available,
        },
    )


@router.post("/groups/{group_id:int}/add-student")
def group_add_student(
    request: Request,
    group_id: int,
    student_id: int = Form(...),
):
    if not _admin_ok(request):
        return RedirectResponse(f"/groups/{group_id}", status_code=303)
    add_student_to_group(group_id, student_id)
    return RedirectResponse(f"/groups/{group_id}", status_code=303)


@router.post("/groups/{group_id:int}/remove-student")
def group_remove_student(
    request: Request,
    group_id: int,
    student_id: int = Form(...),
):
    if not _admin_ok(request):
        return RedirectResponse(f"/groups/{group_id}", status_code=303)
    remove_student_from_group(group_id, student_id)
    return RedirectResponse(f"/groups/{group_id}", status_code=303)
