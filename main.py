from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from src.common.database import init_db
from src.auth.routes import auth_router
from src.profiles.routes import profile_router
from src.match.routes import match_router
from src.dashboard.routes import dashboard_router

templates = Jinja2Templates(directory="templates")
app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(match_router)
app.include_router(dashboard_router)

print(app)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})