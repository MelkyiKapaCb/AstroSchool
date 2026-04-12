from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database.db import init_db
from app.routes.students import router as students_router

app = FastAPI()
app.include_router(students_router)

@app.on_event('startup')
def startup():
    init_db()  # синхронная функция, await не нужен

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')