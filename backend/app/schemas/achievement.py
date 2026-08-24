from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class AchievementOut(BaseModel):
    code: str
    name: str
    description: str
    icon: str
    earned: bool
    earned_at: Optional[datetime]
