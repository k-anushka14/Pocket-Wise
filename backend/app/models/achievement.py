import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from app.database.types import GUID
from sqlalchemy.sql import func

from app.database.session import Base


class Achievement(Base):
    """Fixed catalog of badges -- seeded on startup, not user-created."""
    __tablename__ = "achievements"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, nullable=False)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    achievement_id = Column(GUID(), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
