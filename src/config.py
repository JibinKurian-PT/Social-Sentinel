"""
Central application configuration.
Reads from .env via pydantic-settings and exposes a singleton `settings` object.
All DATABASE_URL values must be literal strings (no shell ${VAR} interpolation).
"""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings  # type: ignore
from pydantic import Field, field_validator  # type: ignore


class Settings(BaseSettings):
    # ── Twitter ──────────────────────────────────────────────────────────────
    TWITTER_BEARER_TOKEN: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_SECRET: str = ""

    # ── YouTube ───────────────────────────────────────────────────────────────
    YOUTUBE_API_KEY: str = ""

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    POSTGRES_USER: str = "sentiment_user"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "sentiment_prod"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Explicit literal URL – never uses ${VAR} style
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v: str, info) -> str:  # type: ignore[override]
        """
        If DATABASE_URL is blank or still uses shell interpolation syntax,
        build it from the individual components instead.
        """
        if v and "${" not in v and v.startswith("postgresql"):
            return v
        # Fall back to constructing from parts
        data = info.data if hasattr(info, "data") else {}
        user = data.get("POSTGRES_USER", "postgres")
        password = data.get("POSTGRES_PASSWORD", "postgres")
        host = data.get("POSTGRES_HOST", "localhost")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "sentiment_prod")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "sentiment_raw"

    # ── Redis / Celery ────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── API Security ──────────────────────────────────────────────────────────
    API_KEY: str = ""
    API_KEY_ENABLED: bool = True

    # ── Ports ─────────────────────────────────────────────────────────────────
    API_PORT: int = 8000
    DASHBOARD_PORT: int = 8501

    # ── NLP / HuggingFace ────────────────────────────────────────────────────
    BERT_MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    HF_HOME: str = "/app/.cache/huggingface"
    
    # NLP Ensemble Tuning
    ENSEMBLE_BERT_WEIGHT: float = 0.7
    ENSEMBLE_TEXTBLOB_WEIGHT: float = 0.3
    
    # Topic Modeling
    LDA_NUM_TOPICS: int = 5

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # ── Mock / Dev Mode ───────────────────────────────────────────────────────
    MOCK_COLLECTORS: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
