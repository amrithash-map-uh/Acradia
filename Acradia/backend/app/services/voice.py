from ..models.schemas import VoiceResponse

LANGUAGE_TO_BCP47 = {
    "en": "en-IN",
    "english": "en-IN",
    "hi": "hi-IN",
    "hindi": "hi-IN",
    "mr": "mr-IN",
    "marathi": "mr-IN",
    "ta": "ta-IN",
    "tamil": "ta-IN",
    "te": "te-IN",
    "telugu": "te-IN",
    "bn": "bn-IN",
    "bengali": "bn-IN",
    "kn": "kn-IN",
    "kannada": "kn-IN",
}


def prepare_speech_payload(text: str, language: str = "en") -> VoiceResponse:
    """Prepare speech synthesis payload; uses browser Web Speech API unless Coqui TTS is configured."""
    normalized = language.strip().lower()
    bcp47 = LANGUAGE_TO_BCP47.get(normalized, "en-IN")
    return VoiceResponse(
        text=text,
        language=language,
        bcp47_lang=bcp47,
        engine="browser_speech_synthesis",
        audio_base64=None,
    )
