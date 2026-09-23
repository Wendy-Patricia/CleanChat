import torch
from functools import lru_cache
from transformers import pipeline
from backend.core.config import get_settings
from backend.core.logging import logger

_PIPE = None #saves the model charged in memory, so we don't have to load it every time we call the function

# decides which device to use for inference: 0 for GPU, -1 for CPU 
def _device() -> int:
    s = get_settings()
    if s.device == "auto":
        return 0 if torch.cuda.is_available() else -1
    return 0 if s.device == "cuda" else -1

def get_pipe():
    global _PIPE
    if _PIPE is None:
        logger.info("Loading sentiment model...")
        _PIPE = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            truncation=True, max_length=512, device=_device(),
        )
        logger.info("Sentiment OK.")
    return _PIPE

# This function is cached to avoid re-running the model for the same text multiple times. The cache size is set to 10,000 entries.
@lru_cache(maxsize=10_000)
def analyze_sentiment(text: str) -> tuple[str, float]:
    if not text.strip():
        return "unknown", 0.0
    r = get_pipe()(text[:512])[0]
    return r["label"].lower(), float(r["score"])

def analyze_sentiment_batch(texts: list[str]) -> list[tuple[str, float]]:
    s = get_settings()
    out: list[tuple[str, float]] = [("unknown", 0.0)] * len(texts)
    to_run, idx = [], []
    for i, t in enumerate(texts):
        if not t.strip():
            continue
        cached = analyze_sentiment.__wrapped__ if hasattr(analyze_sentiment, "__wrapped__") else None

        to_run.append(t[:512]); idx.append(i)

    pipe = get_pipe()
    for start in range(0, len(to_run), s.batch_size):
        chunk = to_run[start:start + s.batch_size]
        preds = pipe(chunk)
        for i, p in zip(idx[start:start + s.batch_size], preds):
            out[i] = (p["label"].lower(), float(p["score"]))
    return out