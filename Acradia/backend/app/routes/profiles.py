from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..models.db_models import UserProfile
from ..models.schemas import ProfileCreate, ProfileOut

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    """Save a citizen profile for scheme discovery."""
    profile = UserProfile(
        name=payload.name,
        age=payload.age,
        income=payload.income,
        location=payload.location.strip(),
        occupation=payload.occupation.strip(),
        preferred_language=payload.preferred_language.strip() or "en",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=List[ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    """List recently created user profiles."""
    return db.query(UserProfile).order_by(UserProfile.id.desc()).limit(20).all()
