"""
Ensures the fixed achievement catalog exists in the DB. Runs once at
startup -- inserts any badge from ACHIEVEMENT_CATALOG that isn't already
there by code, never overwrites existing rows.
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.achievement import Achievement
from app.services.achievements_service import ACHIEVEMENT_CATALOG


def seed_achievement_catalog(db: Session) -> None:
    existing_codes = set(db.execute(select(Achievement.code)).scalars().all())
    for badge in ACHIEVEMENT_CATALOG:
        if badge["code"] not in existing_codes:
            db.add(Achievement(
                id=uuid.uuid4(),
                code=badge["code"],
                name=badge["name"],
                description=badge["description"],
                icon=badge["icon"],
            ))
    db.commit()
