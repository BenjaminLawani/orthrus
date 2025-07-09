from uuid import UUID
import random
import string
from datetime import (
    datetime,
    timedelta,
    UTC
)
from passlib.context import CryptContext
from jwt import (
    encode,
    decode,
    PyJWTError
)
from sqlalchemy.orm import Session
from fastapi import (
    HTTPException,
    Depends,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from .config import settings
from .database import get_db
from src.auth.models import User

ctx = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_VERSION}/auth/login")

def jwt_encode(data: dict):
    return encode(data, settings.JWT_KEY, "HS256")

def jwt_decode(token: str):
    return decode(token, settings.JWT_KEY, ["HS256"])

def hash_password(plain_password: str):
    return ctx.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str):
    return ctx.verify(plain_password, hashed_password)

def generate_otp_code():
    return random.randint(100000, 999999)

# FIXED: Added default value for expires_delta parameter
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.TOKEN_EXPIRES)
    to_encode.update({"exp":expire})
    encoded = jwt_encode(to_encode)
    return encoded

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}    
        )
    try:
        payload = jwt_decode(token)
        user_id : str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = db.query(User).filter((User.id) == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT
        )
    return user