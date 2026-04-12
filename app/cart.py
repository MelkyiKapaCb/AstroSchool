from typing import Any

from starlette.requests import Request

from database.db import get_item


def _cart(request: Request) -> dict[str, int]:
    raw = request.session.get("cart")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, int] = {}
    for k, v in raw.items():
        try:
            q = int(v)
        except (TypeError, ValueError):
            continue
        if q > 0:
            out[str(k)] = q
    return out


def set_cart(request: Request, cart: dict[str, int]) -> None:
    request.session["cart"] = cart


def cart_add(request: Request, item_id: int, qty: int = 1) -> None:
    cart = _cart(request)
    key = str(item_id)
    cart[key] = cart.get(key, 0) + max(1, qty)
    set_cart(request, cart)


def cart_set_line(request: Request, item_id: int, qty: int) -> None:
    cart = _cart(request)
    key = str(item_id)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    set_cart(request, cart)


def cart_clear(request: Request) -> None:
    request.session.pop("cart", None)


def cart_lines(request: Request) -> list[dict[str, Any]]:
    cart = _cart(request)
    lines = []
    for key, qty in cart.items():
        row = get_item(int(key))
        if row is None:
            continue
        price = int(row["price"])
        lines.append(
            {
                "item": row,
                "qty": qty,
                "line_total": price * qty,
            }
        )
    return lines


def cart_total(request: Request) -> int:
    return sum(line["line_total"] for line in cart_lines(request))
