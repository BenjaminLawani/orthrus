from fastapi import FastAPI

from src.common.database import init_db
from src.auth.routes import auth_router
from src.profiles.routes import profile_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router)
app.include_router(profile_router)