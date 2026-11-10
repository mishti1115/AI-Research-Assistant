"""
Summary and comparison endpoints (direct, non-agent-routed access to those
workflows — useful for dedicated UI buttons like "Generate Executive Summary").
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.models.schemas import (
    CompareRequest, CompareResponse, SummaryRequest, SummaryResponse,
)
from app.services import paper_registry, rag_service

router = APIRouter(prefix="/api", tags=["summary"])
settings = get_settings()


@router.post("/summary", response_model=SummaryResponse)
async def summarize(req: SummaryRequest):
    paper = paper_registry.get(req.paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    if paper.status != "ready":
        raise HTTPException(status_code=409, detail=f"Paper is not ready (status={paper.status}).")

    content, sources = rag_service.generate_summary(req.paper_id, req.summary_type, settings.TOP_K)
    return SummaryResponse(
        paper_id=req.paper_id, summary_type=req.summary_type, content=content, sources=sources
    )


@router.post("/compare", response_model=CompareResponse)
async def compare(req: CompareRequest):
    if len(req.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 paper_ids to compare.")
    for pid in req.paper_ids:
        if not paper_registry.get(pid):
            raise HTTPException(status_code=404, detail=f"Unknown paper_id: {pid}")

    top_k_each = max(2, settings.TOP_K // len(req.paper_ids))
    table, sources = rag_service.generate_comparison(req.paper_ids, req.aspects, top_k_each)
    return CompareResponse(paper_ids=req.paper_ids, table_markdown=table, sources=sources)
