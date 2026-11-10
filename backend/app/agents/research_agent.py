"""
Research Agent.

A lightweight decision layer that inspects an incoming natural-language
request and decides: single-paper vs multi-paper, whether comparison is
needed, and which prompt template applies. This keeps a single flexible
"/agent/query" endpoint usable from the frontend's chat box, instead of
forcing the user to pick the right specialized endpoint themselves.

This is deliberately implemented as explicit, inspectable rules rather than
an opaque LLM-only router — it's fast, free, debuggable, and covers the
well-defined intents this app supports. It can be swapped for a LangGraph
StateGraph with an LLM-based router node without changing its interface
(decide() -> AgentDecision), which is the extension point for Phase 2.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from app.services import paper_registry


class WorkflowType(str, Enum):
    CHAT = "chat"
    SUMMARY = "summary"
    COMPARE = "compare"
    LITERATURE_REVIEW = "literature_review"
    RESEARCH_GAP = "research_gap"
    CITATION = "citation"


_SUMMARY_KEYWORDS = {
    "executive": ["executive summary", "quick summary", "tl;dr", "tldr"],
    "detailed": ["detailed summary", "full summary", "in depth"],
    "contributions": ["contribution", "key contribution"],
    "methodology": ["methodology", "method used", "approach used", "how does it work"],
    "dataset": ["dataset", "data used", "data set"],
    "results": ["results", "performance", "accuracy", "benchmark"],
    "limitations": ["limitation", "weakness", "drawback"],
    "future_work": ["future work", "future direction", "open problem"],
    "novelty": ["novelty", "novel", "what's new", "what is new"],
    "practical_applications": ["application", "use case", "real world"],
    "eli10": ["explain like i'm 10", "eli5", "eli10", "simple terms", "like i'm a kid"],
    "viva": ["viva", "thesis defense", "defense question"],
    "interview_questions": ["interview question"],
    "quiz": ["quiz", "flashcard", "test my understanding"],
}

_COMPARE_TRIGGERS = ["compare", "comparison", "versus", " vs ", "difference between"]
_LIT_REVIEW_TRIGGERS = ["literature review"]
_GAP_TRIGGERS = ["research gap", "gaps in", "open problem across"]
_CITATION_TRIGGERS = ["cite", "citation", "bibtex", "reference format"]


@dataclass
class AgentDecision:
    workflow: WorkflowType
    summary_type: str | None = None
    paper_ids: list[str] | None = None
    reasoning: str = ""


def decide(query: str, requested_paper_ids: list[str] | None = None) -> AgentDecision:
    """
    Inspect the query text (and any explicitly selected papers) and decide
    which workflow should handle it.
    """
    q = query.lower().strip()
    requested_paper_ids = requested_paper_ids or []

    if any(t in q for t in _CITATION_TRIGGERS):
        return AgentDecision(WorkflowType.CITATION, paper_ids=requested_paper_ids,
                              reasoning="Query mentions citation/reference formatting.")

    if any(t in q for t in _GAP_TRIGGERS):
        ids = requested_paper_ids or paper_registry.all_ready_ids()
        return AgentDecision(WorkflowType.RESEARCH_GAP, paper_ids=ids,
                              reasoning="Query asks about research gaps across papers.")

    if any(t in q for t in _LIT_REVIEW_TRIGGERS):
        ids = requested_paper_ids or paper_registry.all_ready_ids()
        return AgentDecision(WorkflowType.LITERATURE_REVIEW, paper_ids=ids,
                              reasoning="Query explicitly asks for a literature review.")

    if any(t in q for t in _COMPARE_TRIGGERS) or _mentions_multiple_papers(q):
        ids = requested_paper_ids or paper_registry.all_ready_ids()
        return AgentDecision(WorkflowType.COMPARE, paper_ids=ids,
                              reasoning="Query compares multiple papers/concepts.")

    for summary_type, keywords in _SUMMARY_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            ids = requested_paper_ids[:1] if requested_paper_ids else []
            return AgentDecision(WorkflowType.SUMMARY, summary_type=summary_type, paper_ids=ids,
                                  reasoning=f"Query matches the '{summary_type}' summary intent.")

    return AgentDecision(WorkflowType.CHAT, paper_ids=requested_paper_ids,
                          reasoning="No specialized intent matched; defaulting to grounded Q&A chat.")


def _mentions_multiple_papers(query: str) -> bool:
    """Heuristic: 2+ capitalized multi-word phrases or ' and ' between proper nouns."""
    proper_nouns = re.findall(r"\b[A-Z][A-Za-z0-9\-]{2,}\b", query)
    return len(set(proper_nouns)) >= 2
