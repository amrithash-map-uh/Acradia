from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=True)
    age = Column(Integer, nullable=False)
    income = Column(Integer, nullable=False)
    location = Column(String(120), nullable=False)
    occupation = Column(String(120), nullable=False)
    preferred_language = Column(String(40), nullable=False, default="en")
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    benefits = Column(Text, nullable=False)
    eligibility_rules_json = Column(Text, nullable=False)
    application_guidance = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=False)
    last_reviewed = Column(String(40), nullable=False)


class NGO(Base):
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(120), nullable=False)
    city = Column(String(120), nullable=False)
    contact_email = Column(String(200), nullable=False)
    focus_areas = Column(String(300), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    requests = relationship("NGORequest", back_populates="assigned_ngo")


class NGORequest(Base):
    __tablename__ = "ngo_requests"

    id = Column(Integer, primary_key=True, index=True)
    citizen_name = Column(String(120), nullable=False)
    contact_info = Column(String(160), nullable=False)
    location = Column(String(120), nullable=False)
    scheme_slug = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    consent_given = Column(Boolean, nullable=False, default=False)
    status = Column(String(40), nullable=False, default="pending")
    ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    assigned_ngo = relationship("NGO", back_populates="requests")
