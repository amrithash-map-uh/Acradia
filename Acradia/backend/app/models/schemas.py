from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    age: int = Field(..., ge=0, le=120)
    income: int = Field(..., ge=0, description="Annual household income in INR")
    location: str = Field(..., min_length=2, max_length=120)
    occupation: str = Field(..., min_length=2, max_length=120)
    preferred_language: str = Field(default="en", max_length=40)


class ProfileOut(ProfileCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SchemeOut(BaseModel):
    id: int
    slug: str
    name: str
    category: str
    description: str
    benefits: str
    eligibility_rules: Dict[str, Any]
    application_guidance: str
    source_url: str
    last_reviewed: str


class MatchedSchemeOut(BaseModel):
    scheme: SchemeOut
    match_reasons: List[str]


class MatchResponse(BaseModel):
    profile: ProfileCreate
    matched_count: int
    matches: List[MatchedSchemeOut]
    disclaimer: str


class AssistantRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    scheme_slug: Optional[str] = None
    preferred_language: str = "en"


class CitationOut(BaseModel):
    slug: str
    name: str
    source_url: str
    last_reviewed: str


class AssistantResponse(BaseModel):
    answer: str
    citations: List[CitationOut]
    mode: str
    disclaimer: str


class VoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    language: str = "en"


class VoiceResponse(BaseModel):
    text: str
    language: str
    bcp47_lang: str
    engine: str
    audio_base64: Optional[str] = None


class NGOCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    location: str = Field(..., min_length=2, max_length=120)
    city: str = Field(..., min_length=2, max_length=120)
    contact_email: str = Field(..., min_length=4, max_length=200)
    focus_areas: str = Field(..., min_length=2, max_length=300)
    is_available: bool = True


class NGOOut(NGOCreate):
    id: int

    model_config = {"from_attributes": True}


class NGORequestCreate(BaseModel):
    citizen_name: str = Field(..., min_length=2, max_length=120)
    contact_info: str = Field(..., min_length=4, max_length=160)
    location: str = Field(..., min_length=2, max_length=120)
    scheme_slug: Optional[str] = None
    message: str = Field(..., min_length=5, max_length=1500)
    consent_given: bool = Field(..., description="User consent to share request details with an NGO")


class NGORequestStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|assigned|in_progress|resolved)$")


class NGORequestOut(BaseModel):
    id: int
    citizen_name: str
    contact_info: str
    location: str
    scheme_slug: Optional[str]
    message: str
    consent_given: bool
    status: str
    assigned_ngo: Optional[NGOOut] = None
    created_at: datetime

    model_config = {"from_attributes": True}
