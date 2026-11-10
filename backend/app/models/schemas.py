"""
Pydantic models shared across routers and services.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PaperStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Paper(BaseModel):
    """Metadata for a single uploaded paper."""
    paper_id: str
    filename: str
    title: Optional[str] = None
    num_pages: int = 0
    num_chunks: int = 0
    status: PaperStatus = PaperStatus.UPLOADED
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class UploadResponse(BaseModel):
    paper_id: str
    filename: str
    status: PaperStatus


class SourceChunk(BaseModel):
    """A retrieved chunk shown back to the user as a citation."""
    paper_id: str
    paper_title: Optional[str] = None
    page_number: int
    chunk_id: str
    text: str
    score: float


class ChatRequest(BaseModel):
    query: str
    paper_ids: list[str] = Field(default_factory=list, description="Empty = search all papers")
    conversation_id: Optional[str] = None
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    conversation_id: str
    used_papers: list[str]


class SummaryRequest(BaseModel):
    paper_id: str
    summary_type: str = Field(
        default="executive",
        description="executive | detailed | contributions | methodology | limitations | "
                    "future_work | novelty | eli10 | viva | interview_questions | quiz",
    )


class SummaryResponse(BaseModel):
    paper_id: str
    summary_type: str
    content: str
    sources: list[SourceChunk]


class CompareRequest(BaseModel):
    paper_ids: list[str]
    aspects: list[str] = Field(
        default_factory=lambda: ["dataset", "architecture", "accuracy", "novelty",
                                  "limitations", "future_work"]
    )


class CompareResponse(BaseModel):
    paper_ids: list[str]
    table_markdown: str
    sources: list[SourceChunk]


class CitationRequest(BaseModel):
    paper_id: str
    style: str = Field(default="apa", description="apa | ieee | mla | bibtex")


class CitationResponse(BaseModel):
    paper_id: str
    style: str
    citation: str
