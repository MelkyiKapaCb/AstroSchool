from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from database.db import init_db
from app.routes.students import router as students_router
from app.routes.student import router as student_router
from app.routes.shop import router as shop_router

app = FastAPI()
app.include_router(students_router)
app.include_router(student_router)
app.include_router(shop_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root():
    return RedirectResponse(url="/students")


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
