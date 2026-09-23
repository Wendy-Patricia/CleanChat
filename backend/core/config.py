from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    youtube_api_key: str

    # thresholds de toxicidade
    tox_low: float = 0.30
    tox_medium: float = 0.50
    tox_high: float = 0.80

    # limites de processamento
    max_comments: int = 200
    min_text_length: int = 10
    max_text_chars: int = 512

    # batch size para inferência
    batch_size: int = 32

    # cache
    cache_size: int = 10_000

    # device: "auto" | "cpu" | "cuda"
    device: str = "auto"


@lru_cache
def get_settings() -> Settings:
    return Settings()