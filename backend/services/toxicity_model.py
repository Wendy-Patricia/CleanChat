import torch
from detoxify import Detoxify

from backend.core.config import get_settings
from backend.core.logging import logger

_MODEL = None
_CATEGORIAS_ESPECIFICAS = (
    "severe_toxicity", "obscene", "threat", "insult",
    "identity_attack", "sexual_explicit",
)


def _device() -> str | None:
    s = get_settings()
    if s.device == "auto":
        return "cuda" if torch.cuda.is_available() else None
    return "cuda" if s.device == "cuda" else None


def get_model() -> Detoxify:
    global _MODEL
    if _MODEL is None:
        logger.info("Carregando Detoxify multilingual...")
        _MODEL = Detoxify("multilingual", device=_device())
        logger.info("Detoxify OK.")
    return _MODEL


def tox_level(score: float) -> str:
    s = get_settings()
    if score >= s.tox_high:
        return "high"
    if score >= s.tox_medium:
        return "medium"
    if score >= s.tox_low:
        return "low"
    return "clean"


def _normalize(raw: dict) -> dict:
    tox = float(raw["toxicity"])
    motive = max(_CATEGORIAS_ESPECIFICAS, key=lambda k: raw.get(k, 0.0))
    return {
        "toxicity": tox,
        "motive": motive,
        "score_motive": float(raw.get(motive, 0.0)),
        "tox_level": tox_level(tox),
    }


def analyze_toxicity(text: str) -> dict:
    if not text.strip():
        return {"toxicity": 0.0, "motive": "clean", "score_motive": 0.0, "tox_level": "clean"}
    scores = get_model().predict(text[:512])
    return _normalize(scores)


def analyze_toxicity_batch(texts: list[str]) -> list[dict]:
    if not texts:
        return []
    limpos = [t[:512] if t.strip() else "" for t in texts]
    raw = get_model().predict(limpos)
    n = len(limpos)
    out = []
    for i in range(n):
        item = {k: raw[k][i] for k in raw}
        if not limpos[i]:
            out.append({"toxicity": 0.0, "motive": "clean", "score_motive": 0.0, "tox_level": "clean"})
        else:
            out.append(_normalize(item))
    return out