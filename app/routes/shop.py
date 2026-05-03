from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database.db import get_all_item, create_item

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/shop")
def shop_page(request: Request):
    items = get_all_item()
    return templates.TemplateResponse(
        "shop/list.html",
        {"request": request, "items": items},
    )


@router.get("/shop/add")
def shop_add_form(request: Request):
    return templates.TemplateResponse("shop/add.html", {"request": request})


@router.post("/shop/add")
def shop_add(
    name: str = Form(...),
    price: int = Form(0),
):
    create_item(name, price)
    return RedirectResponse("/shop", status_code=303)
