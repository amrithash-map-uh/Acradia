from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..models.db_models import Scheme
from ..models.schemas import MatchResponse, ProfileCreate, SchemeOut
from ..services.eligibility import evaluate_eligibility, scheme_to_schema

router = APIRouter(prefix="/api/schemes", tags=["schemes"])

ELIGIBILITY_DISCLAIMER = (
    "A match indicates that a scheme may be relevant based on available criteria. "
    "It is not an official confirmation of eligibility or benefit approval."
)


@router.get("", response_model=List[SchemeOut])
def list_schemes(db: Session = Depends(get_db)):
    """Return all curated welfare schemes."""
    schemes = db.query(Scheme).order_by(Scheme.id.asc()).all()
    return [scheme_to_schema(s) for s in schemes]


@router.get("/{slug}", response_model=SchemeOut)
def get_scheme(slug: str, db: Session = Depends(get_db)):
    """Return details for a specific scheme by slug."""
    scheme = db.query(Scheme).filter(Scheme.slug == slug).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme_to_schema(scheme)


@router.post("/match", response_model=MatchResponse)
def match_schemes(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Run rule-based eligibility matching for a citizen profile."""
    schemes = db.query(Scheme).order_by(Scheme.id.asc()).all()
    matches = evaluate_eligibility(profile, schemes)
    return MatchResponse(
        profile=profile,
        matched_count=len(matches),
        matches=matches,
        disclaimer=ELIGIBILITY_DISCLAIMER,
    )
