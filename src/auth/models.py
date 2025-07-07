import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import(
    UUID,
    ENUM,
    JSONB,
)
from src.common.enums import UserEnum
from src.common.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(64), nullable=False, index=True, unique=True)
    email = Column(String(256), nullable=False, index=True, unique=True)
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    otp = Column(Integer())
    otp_expires = Column(DateTime(timezone=True))

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(64), nullable=False)
    bio = Column(String(128), nullable=True)
    interests = Column(JSONB(), default={}, nullable=False)
    linkedin_url = Column(String(256), nullable=True)