import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    func,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import (
    UUID,
    ENUM,
)
from src.common.enums import MatchStatus
from src.common.database import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    match_from = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    match_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)    
    status = Column(ENUM(MatchStatus), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    __table_args__ = (
    UniqueConstraint('match_from', 'match_to', name='uq_match_from_to'),
)
