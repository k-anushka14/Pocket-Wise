from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProfileOut(BaseModel):
    id: UUID
    email: Optional[str] = None
    full_name: Optional[str] = None
    college: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    college: Optional[str] = None
