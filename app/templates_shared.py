from starlette.requests import Request

from database.db import get_user_by_id

templates = None  # set by configure_templates()


def user_context(request: Request) -> dict:
    uid = request.session.get("user_id")
    if not uid:
        return {"current_user": None, "is_admin": False}
    try:
        uid_int = int(uid)
    except (TypeError, ValueError):
        return {"current_user": None, "is_admin": False}
    row = get_user_by_id(uid_int)
    if row is None:
        return {"current_user": None, "is_admin": False}
    user = dict(row)
    user.pop("password_hash", None)
    return {"current_user": user, "is_admin": bool(user.get("is_admin"))}


def configure_templates(directory: str):
    from fastapi.templating import Jinja2Templates

    global templates
    templates = Jinja2Templates(
        directory=directory,
        context_processors=[user_context],
    )
    return templates
