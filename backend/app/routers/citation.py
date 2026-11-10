"""
Citation generation endpoint (APA / IEEE / MLA / BibTeX).

Uses whatever title/metadata was extracted at ingestion time. Since PDFs
rarely expose structured author/venue/year metadata reliably, this reference
implementation generates a best-effort citation from the title and flags
that details should be verified — extend with a CrossRef/Semantic Scholar
lookup (by title) for production-accurate citations.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.models.schemas import CitationRequest, CitationResponse
from app.services import paper_registry

router = APIRouter(prefix="/api/citation", tags=["citation"])


@router.post("", response_model=CitationResponse)
async def generate_citation(req: CitationRequest):
    paper = paper_registry.get(req.paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    title = paper.title or paper.filename
    year = datetime.utcnow().year  # placeholder — true pub year isn't reliably extractable from PDF text alone

    citation = _format_citation(title, req.style, year)
    return CitationResponse(paper_id=req.paper_id, style=req.style, citation=citation)


def _format_citation(title: str, style: str, year: int) -> str:
    style = style.lower()
    if style == "apa":
        return f"Author, A. A. ({year}). {title}."
    if style == "ieee":
        return f'A. A. Author, "{title}," {year}.'
    if style == "mla":
        return f'Author, A. A. "{title}." {year}.'
    if style == "bibtex":
        key = "".join(ch for ch in title.split()[0] if ch.isalnum()).lower() or "paper"
        return (
            f"@article{{{key}{year},\n"
            f"  title={{{title}}},\n"
            f"  year={{{year}}}\n"
            f"}}"
        )
    raise HTTPException(status_code=400, detail=f"Unsupported citation style: {style}")
