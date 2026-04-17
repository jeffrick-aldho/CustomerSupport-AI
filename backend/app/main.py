from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import DATA_PATH, LOG_DIR, settings
from .llm import SarvamClient
from .prompts import FRIENDLY_PROMPT, NO_MATCH_RESPONSE, STRICT_PROMPT
from .retriever import BM25PolicyRetriever
from .schemas import GenerateRequest, GenerateResponse, RetrievedDoc


def build_logger() -> logging.Logger:
    logger = logging.getLogger("customer_support")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = build_logger()
app = FastAPI(title="AI-Assisted Customer Support Response Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = BM25PolicyRetriever(DATA_PATH)
sarvam_client = SarvamClient(
    api_key=settings.sarvam_api_key,
    model=settings.sarvam_model,
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/policies")
def list_policies() -> list[dict[str, str]]:
    return [{"title": doc.title, "content": doc.content} for doc in retriever.documents]


@app.post("/api/generate", response_model=GenerateResponse)
def generate_response(payload: GenerateRequest) -> GenerateResponse:
    query = payload.query.strip()
    retrieved = retriever.retrieve(query=query, top_k=3)
    top_score = retrieved[0]["score"] if retrieved else 0.0
    used_fallback = top_score < settings.bm25_min_score

    parameters = {
        "temperature": 0.2 if payload.mode == "strict" else 0.7,
        "max_tokens": 150 if payload.mode == "strict" else 200,
    }

    if used_fallback:
        response_text = NO_MATCH_RESPONSE
        prompt = "No relevant policy found.\nRespond with:\n\"Please escalate this issue to a human support agent.\""
    else:
        docs_text = "\n\n".join(
            [f"Title: {doc['title']}\nContent: {doc['content']}" for doc in retrieved]
        )
        if payload.mode == "strict":
            prompt = STRICT_PROMPT.format(docs=docs_text, query=query)
        else:
            prompt = FRIENDLY_PROMPT.format(docs=docs_text, query=query)
        response_text = sarvam_client.generate(
            prompt=prompt,
            temperature=parameters["temperature"],
            max_tokens=parameters["max_tokens"],
        )

    log_entry = {
        "query": query,
        "mode": payload.mode,
        "retrieved_docs": retrieved,
        "prompt": prompt,
        "parameters": parameters,
        "used_fallback": used_fallback,
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))

    return GenerateResponse(
        response=response_text,
        mode=payload.mode,
        used_fallback=used_fallback,
        prompt=prompt,
        parameters=parameters,
        sources=[RetrievedDoc(**doc) for doc in retrieved],
    )
