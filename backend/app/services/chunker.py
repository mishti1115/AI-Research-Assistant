"""
Chunking service.

Splits per-page text into overlapping chunks sized for embedding, while
preserving the page number each chunk came from (needed for citations).
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.services.pdf_parser import ParsedDocument

settings = get_settings()


@dataclass
class Chunk:
    chunk_id: str
    paper_id: str
    page_number: int
    text: str
    metadata: dict = field(default_factory=dict)


def chunk_document(paper_id: str, parsed: ParsedDocument) -> list[Chunk]:
    """
    Chunk a parsed document page-by-page so every chunk retains an accurate
    page number for citation purposes, using a recursive splitter that
    respects paragraph / sentence boundaries where possible.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Chunk] = []
    for page in parsed.pages:
        page_splits = splitter.split_text(page.text)
        for split_text in page_splits:
            chunk_id = _deterministic_id(paper_id, page.page_number, split_text)
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    paper_id=paper_id,
                    page_number=page.page_number,
                    text=split_text,
                    metadata={"paper_id": paper_id, "page_number": page.page_number},
                )
            )
    return chunks


def _deterministic_id(paper_id: str, page_number: int, text: str) -> str:
    """Stable hash-based id so re-processing the same paper is idempotent."""
    h = hashlib.sha1(f"{paper_id}:{page_number}:{text[:80]}".encode()).hexdigest()[:12]
    return f"{paper_id}-p{page_number}-{h}"
