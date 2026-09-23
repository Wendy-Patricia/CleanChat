from collections import Counter
from datetime import datetime

from backend.core.config import get_settings
from backend.core.logging import logger
from backend.services.youtube_client import extract_video_id, get_comments
from backend.services.preprocess import clean_text, detect_language, should_skip
from backend.services.sentiment_model import analyze_sentiment_batch
from backend.services.toxicity_model import analyze_toxicity_batch


def _parse_dt(s: str | None) -> datetime:
    if not s:
        return datetime.utcnow()
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def process_video(url_or_id: str, max_results: int | None = None) -> dict:
    """
    Pipeline completo:
      URL -> video_id -> comentários brutos -> limpeza -> análise -> resumo
    """
    settings = get_settings()

    # 1) extrair video_id
    try:
        video_id = extract_video_id(url_or_id)
    except ValueError:
        video_id = url_or_id  # usuário já passou o ID direto

    # 2) baixar comentários
    raw_comments = get_comments(video_id, max_results=max_results)
    total = len(raw_comments)

    # 3) filtrar (skip)
    validos: list[dict] = []
    skips: list[dict] = []
    for c in raw_comments:
        text = clean_text(c["text"])
        skip, reason = should_skip(text)
        base = {
            "author": c["author"],
            "text": text,
            "likes": c["likes"],
            "published_at": _parse_dt(c["date"]),
        }
        if skip:
            skip_base = {
                **base,
                "language": "unknown",
                "sentiment": "unknown",
                "sentiment_score": 0.0,
                "toxicity": 0.0,
                "tox_level": "clean",
                "motivo": "clean",
                "score_motivo": 0.0,
                "skipped": True,
                "skip_reason": reason,
            }
            skips.append(skip_base)
        else:
            validos.append(base)

    # 4) batch inference (só nos válidos)
    texts = [c["text"] for c in validos]
    logger.info(f"Analisando {len(texts)} comentários válidos (de {total})")

    sentiments = analyze_sentiment_batch(texts)
    toxicities = analyze_toxicity_batch(texts)

    # 5) montar resultados
    analyzed: list[dict] = []
    for c, (sent_label, sent_score), tox in zip(validos, sentiments, toxicities):
        analyzed.append(
            {
                **c,
                "language": detect_language(c["text"]),
                "sentiment": sent_label,
                "sentiment_score": sent_score,
                **tox,  # toxicity, motivo, score_motivo, tox_level
                "skipped": False,
                "skip_reason": None,
            }
        )

    # 6) resumo
    all_rows = analyzed + skips
    summary = {
        "sentiment": dict(Counter(r["sentiment"] for r in analyzed)),
        "tox_level": dict(Counter(r["tox_level"] for r in analyzed)),
        "top_motive": dict(Counter(r["motive"] for r in analyzed).most_common(5)),
        "avg_toxicity": (
            sum(r["toxicity"] for r in analyzed) / len(analyzed)
            if analyzed
            else 0.0
        ),
        "languages": dict(
            Counter(r["language"] for r in analyzed).most_common(10)
        ),
    }

    high_tox = sum(1 for r in analyzed if r["tox_level"] == "high")

    logger.info(
        f"Vídeo {video_id}: {len(analyzed)} analisados, "
        f"{len(skips)} pulados, {high_tox} alto risco"
    )

    return {
        "video_id": video_id,
        "total_comments": total,
        "processed": len(analyzed),
        "skipped": len(skips),
        "high_toxicity": high_tox,
        "summary": summary,
        "comments": all_rows,
    }