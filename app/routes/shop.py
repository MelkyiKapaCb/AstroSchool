from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database.db import (
    get_all_item,
    create_item,
    get_student_by_id,
    delete_coins,
    get_connection,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _get_student_for_shop(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    if user.get("role") == "student" and user.get("student_id"):
        student = get_student_by_id(user["student_id"])
        return dict(student) if student else None
    return None


@router.get("/shop")
def shop_page(request: Request):
    items = get_all_item()
    student = _get_student_for_shop(request)
    return templates.TemplateResponse(
        "shop/list.html",
        {"request": request, "items": items, "student": student},
    )


@router.get("/shop/add")
def shop_add_form(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") not in ("admin", "teacher"):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("shop/add.html", {"request": request})


@router.post("/shop/add")
def shop_add(
    request: Request,
    name: str = Form(...),
    price: int = Form(0),
):
    user = request.session.get("user")
    if not user or user.get("role") not in ("admin", "teacher"):
        return RedirectResponse("/login", status_code=303)
    create_item(name, price)
    return RedirectResponse("/shop", status_code=303)


@router.post("/shop/buy/{item_id}")
async def shop_buy(
    request: Request,
    item_id: int,
    student_id: int = Form(...),
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if user.get("role") == "student" and user.get("student_id") != student_id:
        return RedirectResponse("/shop?error=unauthorized", status_code=303)

    student = get_student_by_id(student_id)
    if not student:
        return RedirectResponse("/shop?error=student_not_found", status_code=303)

    all_items = {row["id"]: row for row in get_all_item()}
    item = all_items.get(item_id)
    if not item:
        return RedirectResponse("/shop?error=item_not_found", status_code=303)

    price = item["price"]
    if student["coins"] < price:
        return RedirectResponse("/shop?error=not_enough", status_code=303)

    delete_coins(student_id, price)
    conn = get_connection()
    conn.execute(
        "INSERT INTO transactions (student_id, amount, reason) VALUES (?, ?, ?)",
        (student_id, -price, f"Покупка: {item['name']}"),
    )
    conn.commit()
    conn.close()

    if user.get("role") == "student":
        return RedirectResponse(f"/student/{student_id}", status_code=303)
    return RedirectResponse("/shop", status_code=303)
