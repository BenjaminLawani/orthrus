from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query
)
from .models import Match
from .schemas import (
    MatchesResponse,
    MatchResult,
    CompatibilityRequest,
    CompatibilityResponse
)

from src.auth.models import User

from src.common.database import get_db
from src.common.security import get_current_user
from src.common.enums import MatchStatus
from src.common.config import settings
from src.common.utils import find_matches, single_match_analysis

match_router = APIRouter(
    tags=["MATCH"],
    prefix=f"{settings.API_VERSION}/match"
)

@match_router.post("/{target_user_id}")
def swipe_right(
    target_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You cannot match with yourself."
        )
    
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uh oh."
        )
    
    # Check if a match already exists in either direction
    existing_match = db.query(Match).filter(
        ((Match.match_from == current_user.id) & (Match.match_to == target_user_id)) |
        ((Match.match_from == target_user_id) & (Match.match_to == current_user.id))
    ).first()
    
    if existing_match:
        if existing_match.match_from == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Swipe already recorded."
            )
        else:
            # Reverse match exists, this creates a mutual match
            existing_match.status = MatchStatus.ACCEPTED
            new_match = Match(
                match_from=current_user.id,
                match_to=target_user_id,
                status=MatchStatus.ACCEPTED
            )
            db.add(new_match)
            
            try:
                db.commit()
                return {
                    "message": "🎉 It's a match!",
                    "match_id": str(existing_match.id),
                    "matched_user": {
                        "id": str(target_user.id),
                        "name": target_user.name  # Assuming User has name field
                    }
                }
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to record match."
                )
    else:
        # No existing match, create new pending match
        new_match = Match(
            match_from=current_user.id,
            match_to=target_user_id,
            status=MatchStatus.PENDING
        )
        db.add(new_match)
        
        try:
            db.commit()
            return {
                "message": "Swipe recorded. Waiting for other user to match.",
                "match_id": str(new_match.id)
            }
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record swipe."
            )
        
@match_router.get("/", response_model=MatchesResponse)
def get_matches(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50, description="Number of matches to return"),
    current_user: User = Depends(get_current_user)
):
    """Get top matches for a user"""
    matches = find_matches(str(current_user.id, limit))
    
    if not matches:
        raise HTTPException(
            status_code=404, 
            detail="No matches found or user not found"
        )
    
    return MatchesResponse(
        user_id=user_id,
        matches=[MatchResult(**match) for match in matches]
    )

@match_router.post("/compatibility", response_model=CompatibilityResponse)
async def check_compatibility(request: CompatibilityRequest):
    """Check compatibility between two specific users"""
    result = single_match_analysis(request.user1_id, request.user2_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="One or both users not found"
        )
    
    return CompatibilityResponse(**result)