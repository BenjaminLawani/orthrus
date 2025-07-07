from typing import (
    Optional,
    Any,
    List
)
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    UUID4
)

class ProfileCreate(BaseModel):
    role: str
    bio: Optional[str]
    linkedin_url: Optional[str]
    interests: Optional[List[str, Any]]

class ProfileUpdate(BaseModel):
    role: Optional[str]
    bio: Optional[str]
    linkedin_url: Optional[str]
    interests: Optional[List[str, Any]]

class ProfileResponse(BaseModel):
    id: UUID4
    role: str
    bio: Optional[str]
    linkedin_url: Optional[str]
    interests: Optional[List[str, Any]]
