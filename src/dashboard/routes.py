from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.auth.models import User

from src.common.config import settings
from src.common.security import get_current_user

templates = Jinja2Templates(directory="templates")

dashboard_router = APIRouter(
    prefix= f"{settings.API_VERSION}/dashboard",
    tags=["DASHBOARD"]
)

@dashboard_router.get("/")
def display_dashboard_route(
    request: Request,
    current_user: User = Depends(get_current_user)):
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error: {e} occurred while fetching the dashboard"
        )
    
# @dashboard_router.get("/redirect")
# def dashboard_redirect(current_user: User = Depends(get_current_user)):
#     return RedirectResponse(url=f"/{settings.API_VERSION}/dashboard/")