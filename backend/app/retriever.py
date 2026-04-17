from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


@dataclass
class PolicyDoc:
    title: str
    content: str


class BM25PolicyRetriever:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.documents: list[PolicyDoc] = self._load_documents()
        self.corpus_tokens = [tokenize(self._doc_text(doc)) for doc in self.documents]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    def _load_documents(self) -> list[PolicyDoc]:
        if not self.data_path.exists():
            return []
        raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        docs: list[PolicyDoc] = []
        for item in raw:
            title = str(item.get("title", "")).strip()
            content = str(item.get("content", "")).strip()
            if title and content:
                docs.append(PolicyDoc(title=title, content=content))
        return docs

    def _doc_text(self, doc: PolicyDoc) -> str:
        return f"{doc.title}. {doc.content}"

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if not self.bm25 or not self.documents:
            return []

        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:top_k]

        results: list[dict[str, Any]] = []
        for idx, score in ranked:
            doc = self.documents[idx]
            results.append(
                {
                    "title": doc.title,
                    "content": doc.content,
                    "score": float(score),
                }
            )
        return results

