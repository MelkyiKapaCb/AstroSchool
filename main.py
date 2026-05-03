
# from fastapi import FastAPI, Request
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse
# from database.db import init_db
# from app.routes.students import router as students_router
# from app.routes.student import router as student_router 

# app = FastAPI()
# app.include_router(students_router)
# app.include_router(student_router)   

# @app.on_event('startup')
# def startup():
#     init_db()

# @app.get("/")
# async def root():
#     return RedirectResponse(url="/students")

# templates = Jinja2Templates(directory='templates')
# app.mount('/static', StaticFiles(directory='static'), name='static')

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database.db import init_db
from app.routes.students import router as students_router

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
