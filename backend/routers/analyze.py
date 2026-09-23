from fastapi import APIRouter, HTTPException, Query

from backend.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from backend.services.pipeline import process_video

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_video(payload: AnalyzeRequest):
    try:
        result = process_video(payload.url, max_results=payload.max_results)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_response(result)


@router.get("/analyze", response_model=AnalyzeResponse)
def analyze_video_get(
    url: str = Query(..., description="URL ou ID do vídeo"),
    max_results: int = Query(200, ge=1, le=500),
):
    try:
        result = process_video(url, max_results=max_results)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_response(result)


def _to_response(result: dict) -> dict:
    """Reorganiza a saída do pipeline no formato de seções do router antigo."""
    secoes = {
        "positivos": [],
        "negativos_simples": [],
        "cyberbullying": [],
        "neutros": [],
        "ignorados": [],
    }

    for c in result["comments"]:
        if c.get("skipped"):
            secoes["ignorados"].append(c)
            continue

        if c["tox_level"] in ("high", "medium"):
            secoes["cyberbullying"].append(c)
        elif c["sentiment"] == "negative":
            secoes["negativos_simples"].append(c)
        elif c["sentiment"] == "positive":
            secoes["positivos"].append(c)
        else:
            secoes["neutros"].append(c)

    total = result["total_comments"] or 1
    analisados = result["processed"] or 1  # % sobre analisados, não sobre total

    return {
        "video_id": result["video_id"],
        "total_comentarios": result["total_comments"],
        "analisados": result["processed"],
        "ignorados": result["skipped"],
        "pct_negativos": round(len(secoes["negativos_simples"]) / analisados * 100, 1),
        "pct_cyberbullying": round(len(secoes["cyberbullying"]) / analisados * 100, 1),
        "pct_positivos": round(len(secoes["positivos"]) / analisados * 100, 1),
        "pct_neutros": round(len(secoes["neutros"]) / analisados * 100, 1),
        "resumo": result["summary"],
        "secoes": secoes,
    }