from pydantic import BaseModel, Field, EmailStr, UUID4
from src.common.enums import UserEnum
from datetime import datetime
from typing_extensions import List, Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    created_at: datetime
    updated_at: datetime
    interests: Optional[dict]
    preferences: Optional[List[dict]]

class OTPRequest(BaseModel):
    email: EmailStr

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserLogin(BaseModel):
    username: str #Email or Username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
