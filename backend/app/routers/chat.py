"""
Chat endpoints: direct RAG chat, plus the agent-routed "smart" endpoint that
dispatches to chat/summary/compare/etc based on the research agent's decision.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from app.agents.research_agent import WorkflowType, decide
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.schemas import ChatRequest, ChatResponse
from app.services import paper_registry, rag_service

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Grounded Q&A over one or more papers (bypasses the agent — direct RAG call)."""
    _validate_papers(req.paper_ids)
    top_k = req.top_k or settings.TOP_K
    answer, sources = rag_service.answer_query(
        paper_ids=req.paper_ids, query=req.query, history="", top_k=top_k
    )
    used = sorted({s.paper_id for s in sources})
    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=req.conversation_id or str(uuid.uuid4())[:8],
        used_papers=used,
    )


@router.post("/agent", response_model=ChatResponse)
async def agent_chat(req: ChatRequest):
    """
    Natural-language entry point: the research agent decides whether this
    is a chat question, a summary request, a comparison, etc., and routes
    accordingly. The frontend chat box should call this endpoint.
    """
    decision = decide(req.query, req.paper_ids)
    logger.info("Agent routed query to %s (%s)", decision.workflow, decision.reasoning)
    top_k = req.top_k or settings.TOP_K

    if decision.workflow == WorkflowType.SUMMARY and decision.paper_ids:
        content, sources = rag_service.generate_summary(
            decision.paper_ids[0], decision.summary_type or "executive", top_k
        )
        return ChatResponse(
            answer=content, sources=sources,
            conversation_id=req.conversation_id or str(uuid.uuid4())[:8],
            used_papers=decision.paper_ids,
        )

    if decision.workflow == WorkflowType.COMPARE and decision.paper_ids:
        table, sources = rag_service.generate_comparison(decision.paper_ids, [
            "dataset", "architecture", "accuracy", "novelty", "limitations", "future_work"
        ], top_k_per_paper=max(2, top_k // max(1, len(decision.paper_ids))))
        return ChatResponse(
            answer=table, sources=sources,
            conversation_id=req.conversation_id or str(uuid.uuid4())[:8],
            used_papers=decision.paper_ids,
        )

    # Default / fallback: grounded chat (covers CHAT, and CITATION/LITERATURE_REVIEW/
    # RESEARCH_GAP in this reference build — see README "Extension points").
    answer, sources = rag_service.answer_query(
        paper_ids=decision.paper_ids or req.paper_ids, query=req.query, history="", top_k=top_k
    )
    used = sorted({s.paper_id for s in sources})
    return ChatResponse(
        answer=answer, sources=sources,
        conversation_id=req.conversation_id or str(uuid.uuid4())[:8],
        used_papers=used,
    )


def _validate_papers(paper_ids: list[str]) -> None:
    for pid in paper_ids:
        if not paper_registry.get(pid):
            raise HTTPException(status_code=404, detail=f"Unknown paper_id: {pid}")
