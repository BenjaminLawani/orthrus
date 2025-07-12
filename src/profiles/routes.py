from datetime import (
    datetime,
    timedelta,
    UTC,
)
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
)
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from .schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse
)

from src.auth.models import UserProfile, User
from src.common.database import get_db
from src.common.security import get_current_user
from src.common.config import settings

templates = Jinja2Templates(directory="templates")

profile_router = APIRouter(
    tags=["PROFILE"],
    prefix=f"{settings.API_VERSION}/profile"
)

@profile_router.post("/create-profile", response_model=ProfileResponse)
def create_profile(
    request: Request,
    profile: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    print(f"Current user: {str(current_user.id) if current_user else 'None'}")
    print(f"Authorization header: {request.headers.get('authorization', 'Missing')}")
    existing_profile = db.query(UserProfile).filter_by(user_id=current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists",
        )
    
    try:
        new_profile = UserProfile(
            user_id=str(current_user.id),  # Added missing user_id
            role=profile.role,
            bio=profile.bio,
            interests=profile.interests,
            linkedin_url=profile.linkedin_url,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        
        # Return the profile response
        return ProfileResponse(
            id=new_profile.user_id,
            role=new_profile.role,
            bio=new_profile.bio,
            interests=new_profile.interests,
            linkedin_url=new_profile.linkedin_url,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating profile: {str(e)}"
        )
    
@profile_router.get("/create-profile")
def get_create_profile_route(request: Request):
    return templates.TemplateResponse("create-profile.html", {"request":request})