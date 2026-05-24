from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from database.db import get_connection, get_all_item, get_student_by_id, delete_coins

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Хранилище корзин (временное, в реальном проекте используйте БД)
carts = {}

def get_cart(student_id: int):
    """Получает корзину ученика"""
    if student_id not in carts:
        carts[student_id] = []
    return carts[student_id]

def clear_cart(student_id: int):
    """Очищает корзину"""
    if student_id in carts:
        carts[student_id] = []

@router.get("/cart", response_class=HTMLResponse)
async def view_cart(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") not in ["student", "teacher", "admin"]:
        return RedirectResponse("/login", status_code=303)
    
    student_id = None
    if user.get("role") == "student":
        student_id = user.get("student_id")
    elif user.get("role") in ["teacher", "admin"]:
        # Учитель/админ может выбрать ученика
        student_id = request.query_params.get("student_id")
        if student_id:
            student_id = int(student_id)
    
    if not student_id:
        return RedirectResponse("/students", status_code=303)
    
    student = get_student_by_id(student_id)
    cart_items = get_cart(student_id)
    
    # Получаем полную информацию о товарах
    all_items = {item["id"]: item for item in get_all_item()}
    cart_details = []
    total = 0
    
    for item_id in cart_items:
        if item_id in all_items:
            item = all_items[item_id]
            cart_details.append(item)
            total += item["price"]
    
    return templates.TemplateResponse(
        "cart/cart.html",
        {
            "request": request,
            "cart_items": cart_details,
            "total": total,
            "student": dict(student) if student else None,
            "student_id": student_id
        }
    )

@router.post("/cart/add/{item_id}")
async def add_to_cart(
    request: Request,
    item_id: int,
    student_id: int = Form(...)
):
    user = request.session.get("user")
    
    # Проверяем права
    if user.get("role") == "student":
        if user.get("student_id") != student_id:
            return RedirectResponse("/shop?error=unauthorized", status_code=303)
    elif user.get("role") not in ["teacher", "admin"]:
        return RedirectResponse("/login", status_code=303)
    
    cart = get_cart(student_id)
    cart.append(item_id)
    
    return RedirectResponse("/cart?student_id=" + str(student_id), status_code=303)

@router.post("/cart/remove/{item_id}")
async def remove_from_cart(
    request: Request,
    item_id: int,
    student_id: int = Form(...)
):
    user = request.session.get("user")
    
    if user.get("role") == "student" and user.get("student_id") != student_id:
        return RedirectResponse("/shop?error=unauthorized", status_code=303)
    
    cart = get_cart(student_id)
    if item_id in cart:
        cart.remove(item_id)
    
    return RedirectResponse("/cart?student_id=" + str(student_id), status_code=303)

@router.post("/cart/clear")
async def clear_cart_route(
    request: Request,
    student_id: int = Form(...)
):
    user = request.session.get("user")
    
    if user.get("role") == "student" and user.get("student_id") != student_id:
        return RedirectResponse("/shop?error=unauthorized", status_code=303)
    
    clear_cart(student_id)
    return RedirectResponse("/cart?student_id=" + str(student_id), status_code=303)

@router.post("/cart/checkout")
async def checkout(
    request: Request,
    student_id: int = Form(...)
):
    user = request.session.get("user")
    
    # Проверяем права
    if user.get("role") == "student":
        if user.get("student_id") != student_id:
            return RedirectResponse("/cart?error=unauthorized", status_code=303)
    elif user.get("role") not in ["teacher", "admin"]:
        return RedirectResponse("/login", status_code=303)
    
    student = get_student_by_id(student_id)
    cart_items = get_cart(student_id)
    
    if not cart_items:
        return RedirectResponse("/cart?student_id=" + str(student_id) + "&error=empty", status_code=303)
    
    # Получаем все товары
    all_items = {item["id"]: item for item in get_all_item()}
    total = 0
    
    for item_id in cart_items:
        if item_id in all_items:
            total += all_items[item_id]["price"]
    
    # Проверяем достаточно ли монет
    if student["coins"] < total:
        return RedirectResponse("/cart?student_id=" + str(student_id) + "&error=not_enough", status_code=303)
    
    # Списываем монеты
    delete_coins(student_id, total)
    
    # Записываем транзакцию
    conn = get_connection()
    conn.execute(
        "INSERT INTO transactions (student_id, amount, reason) VALUES (?, ?, ?)",
        (student_id, -total, f"Покупка {len(cart_items)} товаров")
    )
    conn.commit()
    conn.close()
    
    # Очищаем корзину
    clear_cart(student_id)
    
    return RedirectResponse("/cart?student_id=" + str(student_id) + "&success=bought", status_code=303)