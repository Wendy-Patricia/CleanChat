from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Sentiment = Literal["positive", "neutral", "negative", "unknown"]
ToxLevel = Literal["clean", "low", "medium", "high"]


class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="URL ou ID do vídeo do YouTube")
    max_results: int = Field(200, ge=1, le=500)


class CommentAnalysis(BaseModel):
    author: str
    text: str
    language: str = "unknown"
    sentiment: Sentiment = "unknown"
    sentiment_score: float = 0.0
    toxicity: float = Field(0.0, ge=0.0, le=1.0)
    tox_level: ToxLevel = "clean"
    motivo: str = "clean"
    score_motivo: float = 0.0
    likes: int = 0
    published_at: datetime | None = None
    skipped: bool = False
    skip_reason: str | None = None


class Sections(BaseModel):
    positivos: list[CommentAnalysis]
    negativos_simples: list[CommentAnalysis]
    cyberbullying: list[CommentAnalysis]
    neutros: list[CommentAnalysis]
    ignorados: list[CommentAnalysis] = []


class AnalyzeResponse(BaseModel):
    video_id: str
    total_comentarios: int
    analisados: int
    ignorados: int
    pct_positivos: float
    pct_negativos: float
    pct_neutros: float
    pct_cyberbullying: float
    resumo: dict
    secoes: Sections