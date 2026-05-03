from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from database.db import get_all_students, get_connection, get_student_by_id, update_student

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/students", response_class=HTMLResponse)
async def list_students(request: Request):
    students = get_all_students()
    return templates.TemplateResponse(
        "students/list.html",
        {"request": request, "students": students},
    )


@router.get("/students/add")
def add_student_form(request: Request):
    return templates.TemplateResponse("students/add.html", {"request": request})


@router.post("/students/add")
async def add_student(
    request: Request,
    name: str = Form(...),
    class_name: str = Form(""),
    coins: int = Form(0),
    data: str = Form(""),
):
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (name, coins, class, data) VALUES (?, ?, ?, ?)",
        (name, coins, class_name, data),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/students", status_code=303)


@router.delete("/students/delete/{student_id}")
async def delete_student_ajax(student_id: int):
    try:
        conn = get_connection()
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Студент не найден")
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return JSONResponse(status_code=200, content={"message": "OK"})
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/students/edit/{student_id}")
async def edit_student_form(request: Request, student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        return RedirectResponse("/students", status_code=303)
    return templates.TemplateResponse(
        "students/edit.html", {"request": request, "student": student}
    )


@router.post("/students/edit/{student_id}")
async def edit_student(
    student_id: int,
    name: str = Form(...),
    class_name: str = Form(""),
):
    update_student(student_id, name, class_name)
    return RedirectResponse("/students", status_code=303)
