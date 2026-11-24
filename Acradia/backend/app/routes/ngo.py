from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..database.db import get_db
from ..models.db_models import NGO, NGORequest
from ..models.schemas import (
    NGOCreate,
    NGOOut,
    NGORequestCreate,
    NGORequestOut,
    NGORequestStatusUpdate,
)

router = APIRouter(prefix="/api", tags=["ngo"])


def _find_matching_ngo(location: str, db: Session) -> Optional[NGO]:
    """Match an available registered NGO by location/city, falling back to All India."""
    available = db.query(NGO).filter(NGO.is_available.is_(True)).all()
    if not available:
        return None

    loc_norm = location.strip().lower()
    for ngo in available:
        ngo_loc = ngo.location.strip().lower()
        ngo_city = ngo.city.strip().lower()
        if ngo_loc != "all india" and (
            ngo_loc in loc_norm or loc_norm in ngo_loc or ngo_city in loc_norm or loc_norm in ngo_city
        ):
            return ngo

    for ngo in available:
        if ngo.location.strip().lower() == "all india":
            return ngo

    return None


@router.get("/ngos", response_model=List[NGOOut])
def list_ngos(db: Session = Depends(get_db)):
    """List registered NGOs."""
    return db.query(NGO).order_by(NGO.id.asc()).all()


@router.post("/ngos", response_model=NGOOut, status_code=status.HTTP_201_CREATED)
def register_ngo(payload: NGOCreate, db: Session = Depends(get_db)):
    """Register a new NGO partner."""
    ngo = NGO(**payload.model_dump())
    db.add(ngo)
    db.commit()
    db.refresh(ngo)
    return ngo


@router.get("/ngo/requests", response_model=List[NGORequestOut])
def list_help_requests(db: Session = Depends(get_db)):
    """List submitted citizen help requests and their routing status."""
    return (
        db.query(NGORequest)
        .options(joinedload(NGORequest.assigned_ngo))
        .order_by(NGORequest.id.desc())
        .all()
    )


@router.post("/ngo/requests", response_model=NGORequestOut, status_code=status.HTTP_201_CREATED)
def create_help_request(payload: NGORequestCreate, db: Session = Depends(get_db)):
    """Submit a help request with explicit user consent and route to an available NGO."""
    if not payload.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit user consent is required before sharing details with an NGO.",
        )

    matched_ngo = _find_matching_ngo(payload.location, db)
    help_request = NGORequest(
        citizen_name=payload.citizen_name.strip(),
        contact_info=payload.contact_info.strip(),
        location=payload.location.strip(),
        scheme_slug=payload.scheme_slug,
        message=payload.message.strip(),
        consent_given=True,
        status="assigned" if matched_ngo else "pending",
        ngo_id=matched_ngo.id if matched_ngo else None,
    )
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    return (
        db.query(NGORequest)
        .options(joinedload(NGORequest.assigned_ngo))
        .filter(NGORequest.id == help_request.id)
        .one()
    )


@router.patch("/ngo/requests/{request_id}", response_model=NGORequestOut)
def update_help_request_status(
    request_id: int,
    payload: NGORequestStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the status of an NGO help request."""
    help_request = (
        db.query(NGORequest)
        .options(joinedload(NGORequest.assigned_ngo))
        .filter(NGORequest.id == request_id)
        .first()
    )
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found")

    help_request.status = payload.status
    db.commit()
    db.refresh(help_request)
    return help_request
