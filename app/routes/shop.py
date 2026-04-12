from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.cart import cart_add, cart_clear, cart_lines, cart_set_line, cart_total
from app.templates_shared import templates
from database.db import (
    create_item,
    delete_coins,
    get_all_items,
    get_item,
    get_student_by_user_id,
    get_user_by_id,
)

router = APIRouter()


@router.get("/shop")
def shop_list(request: Request):
    items = get_all_items()
    return templates.TemplateResponse(
        request,
        "shop/list.html",
        {"items": items},
    )


@router.get("/shop/{item_id:int}")
def shop_item(request: Request, item_id: int):
    item = get_item(item_id)
    if item is None:
        return RedirectResponse("/shop", status_code=303)
    return templates.TemplateResponse(
        request,
        "shop/detail.html",
        {"item": item},
    )


@router.post("/shop/add")
def shop_add_item(
    request: Request,
    name: str = Form(...),
    price: int = Form(10),
    description: str = Form(""),
):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)
    u = get_user_by_id(int(request.session["user_id"]))
    if u is None or not u["is_admin"]:
        return RedirectResponse("/shop", status_code=303)
    create_item(name, price=price, description=description)
    return RedirectResponse("/shop", status_code=303)


@router.get("/cart")
def cart_page(request: Request):
    lines = cart_lines(request)
    total = sum(ln["line_total"] for ln in lines)
    return templates.TemplateResponse(
        request,
        "shop/cart.html",
        {
            "lines": lines,
            "cart_total": total,
            "checkout_ok": request.query_params.get("ok"),
        },
    )


@router.post("/cart/add")
def cart_add_route(
    request: Request,
    item_id: int = Form(...),
    qty: int = Form(1),
):
    if get_item(item_id) is None:
        return RedirectResponse("/shop", status_code=303)
    cart_add(request, item_id, qty)
    return RedirectResponse(f"/shop/{item_id}", status_code=303)


@router.post("/cart/update")
def cart_update(
    request: Request,
    item_id: int = Form(...),
    qty: int = Form(0),
):
    cart_set_line(request, item_id, qty)
    return RedirectResponse("/cart", status_code=303)


@router.post("/cart/checkout")
def cart_checkout(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=303)
    student = get_student_by_user_id(int(uid))
    if student is None:
        return RedirectResponse("/profile", status_code=303)
    total = cart_total(request)
    if total <= 0:
        return RedirectResponse("/cart", status_code=303)
    if int(student["coins"]) < total:
        return templates.TemplateResponse(
            request,
            "shop/cart.html",
            {
                "lines": cart_lines(request),
                "cart_total": total,
                "error": "Недостаточно монет для оформления заказа.",
            },
        )
    delete_coins(student["id"], total)
    cart_clear(request)
    return RedirectResponse("/cart?ok=1", status_code=303)
