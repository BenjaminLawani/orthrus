from pydantic import BaseModel
from typing import List
class CompatibilityRequest(BaseModel):
    user1_id: str
    user2_id: str

class MatchResult(BaseModel):
    user_id: str
    compatibility_score: float
    rationale: str

class MatchesResponse(BaseModel):
    user_id: str
    matches: List[MatchResult]

class CompatibilityResponse(BaseModel):
    user1_id: str
    user2_id: str
    compatibility_score: float
    rationale: str
