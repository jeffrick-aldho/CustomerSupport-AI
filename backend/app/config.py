from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "policies.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(dotenv_path=BASE_DIR / ".env")


def _csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    sarvam_api_key: str = os.getenv("SARVAM_API_KEY", "")
    sarvam_model: str = os.getenv("SARVAM_MODEL", "sarvam-default-model")
    cors_origins: list[str] = _csv_env("BACKEND_CORS_ORIGINS", "http://localhost:5173")
    bm25_min_score: float = float(os.getenv("BM25_MIN_SCORE", "0.1"))


settings = Settings()
