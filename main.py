from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database.db import init_db
from app.routes.students import router as students_router
from fastapi.responses import RedirectResponse

app = FastAPI()
app.include_router(students_router)

@app.on_event('startup')
def startup():
    init_db()

@app.get("/")
async def root():
    return RedirectResponse(url="/students")

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')  
