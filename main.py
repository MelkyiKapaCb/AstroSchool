import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.templates_shared import configure_templates
from database.db import init_db

configure_templates("templates")

from app.routes.auth import router as auth_router
from app.routes.groups import router as groups_router
from app.routes.pages import router as pages_router
from app.routes.shop import router as shop_router
from app.routes.students import router as students_router

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "astro-school-dev-secret-change-me"),
)

app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(shop_router)
app.include_router(groups_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    init_db()
