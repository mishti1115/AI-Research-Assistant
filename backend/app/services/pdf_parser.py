"""
PDF parsing service.

Extracts per-page text (and basic metadata) from a PDF using PyMuPDF (fitz).
Falls back gracefully and raises a clear error if the file can't be parsed.
"""
from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF

from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PageText:
    page_number: int  # 1-indexed, matches what a human sees in the PDF
    text: str


@dataclass
class ParsedDocument:
    title: str | None
    num_pages: int
    pages: list[PageText]


class PDFParsingError(Exception):
    """Raised when a PDF cannot be parsed or contains no extractable text."""


def parse_pdf(file_path: str) -> ParsedDocument:
    """
    Extract text from every page of a PDF.

    Raises:
        PDFParsingError: if the file is corrupt or has no extractable text
            (e.g. it's a pure scanned image with no OCR layer).
    """
    try:
        doc = fitz.open(file_path)
    except Exception as exc:  # noqa: BLE001 - we want to wrap any parser failure
        logger.error("Failed to open PDF %s: %s", file_path, exc)
        raise PDFParsingError(f"Could not open PDF: {exc}") from exc

    pages: list[PageText] = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        text = _clean_text(text)
        if text:
            pages.append(PageText(page_number=i, text=text))

    title = _extract_title(doc)
    num_pages = doc.page_count
    doc.close()

    if not pages:
        raise PDFParsingError(
            "No extractable text found. This may be a scanned PDF that requires OCR."
        )

    logger.info("Parsed PDF %s: %d pages, %d with text", file_path, num_pages, len(pages))
    return ParsedDocument(title=title, num_pages=num_pages, pages=pages)


def _extract_title(doc: "fitz.Document") -> str | None:
    """Try metadata title first, then fall back to the first line of page 1."""
    meta_title = (doc.metadata or {}).get("title", "").strip()
    if meta_title:
        return meta_title
    if doc.page_count > 0:
        first_page_text = doc[0].get_text("text") or ""
        lines = [l.strip() for l in first_page_text.splitlines() if l.strip()]
        if lines:
            return lines[0][:200]
    return None


def _clean_text(text: str) -> str:
    """Normalize whitespace and strip common PDF extraction artifacts."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    cleaned = "\n".join(lines)
    # Collapse excessive spacing introduced by column-based PDF layouts
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    return cleaned.strip()
