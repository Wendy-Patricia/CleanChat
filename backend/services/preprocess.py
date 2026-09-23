import re
from langdetect import detect, LangDetectException, DetectorFactory

from backend.core.config import get_settings

DetectorFactory.seed = 0  # deterministic behavior

_URL_RE = re.compile(r"(https?://\S+|www\.\S+)")
_MENTION_RE = re.compile(r"(?<!\w)@\w+")
_WS_RE = re.compile(r"\s+")
_REPEAT_RE = re.compile(r"(.)\1{3,}")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = _URL_RE.sub(" ", text)
    text = _MENTION_RE.sub(" ", text)
    text = _REPEAT_RE.sub(r"\1\1", text)
    text = _WS_RE.sub(" ", text).strip()
    return text


def detect_language(text: str) -> str:
    settings = get_settings()
    if len(text.strip()) < settings.min_text_length:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def should_skip(text: str) -> tuple[bool, str | None]:
    """Returns (skip?, reason)."""
    settings = get_settings()
    if not text.strip():
        return True, "empty"
    if len(text.strip()) < settings.min_text_length:
        return True, "too_short"
    if detect_language(text) == "unknown":
        return True, "unknown_language"
    return False, None