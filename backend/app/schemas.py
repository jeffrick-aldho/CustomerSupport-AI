from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ModeType = Literal["strict", "friendly"]


class GenerateRequest(BaseModel):
    query: str = Field(min_length=1, description="Customer complaint or issue")
    mode: ModeType = Field(default="strict")


class RetrievedDoc(BaseModel):
    title: str
    content: str
    score: float


class GenerateResponse(BaseModel):
    response: str
    mode: ModeType
    used_fallback: bool
    prompt: str
    parameters: dict
    sources: list[RetrievedDoc]

