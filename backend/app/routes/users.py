from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.profile import Profile
from app.schemas.profile import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/me", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.get(Profile, current_user.id)
    if not profile:
        # First call after signup -- create an empty profile row on the fly.
        profile = Profile(id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileOut(
        id=profile.id,
        email=current_user.email,
        full_name=profile.full_name,
        college=profile.college,
        created_at=profile.created_at,
    )


@router.put("", response_model=ProfileOut)
def update_my_profile(
    payload: ProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.get(Profile, current_user.id)
    if not profile:
        profile = Profile(id=current_user.id)
        db.add(profile)

    if payload.full_name is not None:
        profile.full_name = payload.full_name
    if payload.college is not None:
        profile.college = payload.college

    db.commit()
    db.refresh(profile)

    return ProfileOut(
        id=profile.id,
        email=current_user.email,
        full_name=profile.full_name,
        college=profile.college,
        created_at=profile.created_at,
    )
