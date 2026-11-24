from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..models.db_models import Scheme
from ..models.schemas import (
    AssistantRequest,
    AssistantResponse,
    VoiceRequest,
    VoiceResponse,
)
from ..services.retrieval import answer_question
from ..services.voice import prepare_speech_payload

router = APIRouter(prefix="/api", tags=["assistant"])


@router.post("/assistant/ask", response_model=AssistantResponse)
def ask_assistant(payload: AssistantRequest, db: Session = Depends(get_db)):
    """Answer citizen questions grounded in the curated scheme knowledge base."""
    schemes = db.query(Scheme).all()
    return answer_question(
        question=payload.question,
        schemes=schemes,
        scheme_slug=payload.scheme_slug,
        preferred_language=payload.preferred_language,
    )


@router.post("/voice/speak", response_model=VoiceResponse)
def speak_text(payload: VoiceRequest):
    """Prepare text-to-speech metadata/audio for scheme explanations."""
    return prepare_speech_payload(text=payload.text, language=payload.language)
