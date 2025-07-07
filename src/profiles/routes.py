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
from .schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse
)

from src.auth.models import UserProfile, User
from src.common.database import get_db
from src.common.security import get_current_user
from src.common.config import settings


profile_router = APIRouter(
    tags=["PROFILE"],
    prefix = f"{settings.API_VERSION}/profile"
)

@profile_router.post("/", response_model=ProfileResponse)
def create_profile(
    request: Request,
    profile: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    existing_profile = db.query(UserProfile).filter_by(user_id=current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists",
        )
    try:
        new_profile = UserProfile(
            role = profile.role,
            bio = profile.bio,
            interests = profile.interests,
            linkedin_url = profile.linkedin_url,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"An error: {e}, occurred."
        )
    