from datetime import (
    datetime,
    UTC,
    timedelta
)
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Request
)
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from .schemas import (
    UserCreate,
    UserLogin,
    UserForgotPassword,
    UserResponse,
    OTPRequest,
    Token
)
from .models import User
from src.common.utils import fm
from src.common.config import settings
from src.common.database import get_db
from src.common.security import (
    verify_password,
    hash_password,
    generate_otp_code,
    get_current_user,
    create_access_token
)


auth_router = APIRouter(
    tags=["AUTHENTICATION"],
    prefix = f"{settings.API_VERSION}/auth"
)


@auth_router.post("/login", response_model=Token)
def login_route(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter((User.username==form_data.username) | (User.email == form_data.username)).first()
    # FIXED: Changed 'or' to 'and' for proper password verification
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials."
        )
    access_token = create_access_token(
        data={
            "sub": str(db_user.id),
            "email": db_user.email,
        }
    )
    return {"access_token":access_token, "token_type": "bearer"}

@auth_router.post("/get-started", response_model=UserResponse)
def create_new_user_route(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    new_user = User(
        email = user_data.email,
        username = user_data.username,
        password = hash_password(user_data.password),
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        # FIXED: Added parentheses to db.rollback()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error {e} occurred while creating this user."
        )
    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
    )
    
@auth_router.post("/request-otp", response_model=dict)
async def request_otp_code(
    request: Request,
    user: OTPRequest,
    db: Session = Depends(get_db), 
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not exist."
        )
    try:
        otp = generate_otp_code()
        expires = datetime.now(UTC) + timedelta(minutes=5)

        db_user.otp = otp
        db_user.otp_expiry = expires
        db.commit()

        email_content = f"""
        Your OTP code is: {otp}
        
        This code will expire in 5 minutes.
        """
        
        await fm.send_email(
            subject="Your OTP Code",
            recipients=[user.email],
            body=email_content
        )
        
        return {"message": "OTP sent successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )
    # REMOVED: Duplicate exception block
    
@auth_router.post("/validate-otp")
def validate_otp_route(
    user: UserCreate,
    otp: str,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check OTP existence
    if not db_user.otp or not db_user.otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP request found"
        )
    
    # Check OTP expiration
    current_time = datetime.now(UTC)
    if current_time > db_user.otp_expiry:
        # Clear expired OTP
        db_user.otp = None
        db_user.otp_expiry = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired"
        )
    
    # Validate OTP
    if db_user.otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    try:
        # Clear used OTP
        db_user.otp = None
        db_user.otp_expiry = None
        # Set user as verified
        db_user.is_verified = True
        db.commit()
        
        return {"message": "OTP verified successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"OTP validation failed: {str(e)}"
        )