"""
RAG orchestration service.

Two responsibilities:
1. ingest_paper(): runs the full pipeline (parse -> chunk -> embed -> index)
2. answer_query(): retrieves relevant chunks and generates a grounded answer

This is the module the agent (app/agents/research_agent.py) and the API
routers call into — it has no HTTP-specific code so it's independently testable.
"""
from __future__ import annotations

import uuid

from app.core.logging_config import get_logger
from app.models.schemas import Paper, PaperStatus, SourceChunk
from app.prompts import templates
from app.services import llm_service, paper_registry, vector_store
from app.services.chunker import chunk_document
from app.services.pdf_parser import PDFParsingError, parse_pdf

logger = get_logger(__name__)


def ingest_paper(file_path: str, filename: str) -> Paper:
    """Run the full ingestion pipeline for a single uploaded PDF."""
    paper_id = str(uuid.uuid4())[:8]
    paper = Paper(paper_id=paper_id, filename=filename, status=PaperStatus.PROCESSING)
    paper_registry.save(paper)

    try:
        parsed = parse_pdf(file_path)
        chunks = chunk_document(paper_id, parsed)
        vector_store.build_index(paper_id, chunks)

        paper.title = parsed.title or filename
        paper.num_pages = parsed.num_pages
        paper.num_chunks = len(chunks)
        paper.status = PaperStatus.READY
        logger.info("Paper %s (%s) ingested: %d pages, %d chunks",
                    paper_id, paper.title, paper.num_pages, paper.num_chunks)

    except PDFParsingError as exc:
        paper.status = PaperStatus.FAILED
        paper.error = str(exc)
        logger.error("Ingestion failed for %s: %s", filename, exc)
    except Exception as exc:  # noqa: BLE001
        paper.status = PaperStatus.FAILED
        paper.error = f"Unexpected error: {exc}"
        logger.exception("Unexpected ingestion failure for %s", filename)

    paper_registry.save(paper)
    return paper


def retrieve(paper_ids: list[str], query: str, top_k: int) -> list[SourceChunk]:
    """Retrieve the top-k most relevant chunks across the given papers."""
    target_ids = paper_ids or paper_registry.all_ready_ids()
    hits = vector_store.similarity_search(target_ids, query, top_k)

    sources: list[SourceChunk] = []
    for doc, score in hits:
        pid = doc.metadata.get("paper_id", "")
        paper = paper_registry.get(pid)
        sources.append(
            SourceChunk(
                paper_id=pid,
                paper_title=paper.title if paper else None,
                page_number=doc.metadata.get("page_number", -1),
                chunk_id=doc.metadata.get("chunk_id", ""),
                text=doc.page_content,
                score=round(float(score), 4),
            )
        )
    return sources


def build_context(sources: list[SourceChunk]) -> str:
    """Format retrieved chunks into a labeled context block for prompting."""
    blocks = []
    for s in sources:
        label = f"[{s.paper_title or s.paper_id}, page {s.page_number}]"
        blocks.append(f"{label}\n{s.text}")
    return "\n\n---\n\n".join(blocks) if blocks else "(no relevant context found)"


def answer_query(paper_ids: list[str], query: str, history: str, top_k: int) -> tuple[str, list[SourceChunk]]:
    """Retrieve + generate: the core RAG chat call."""
    sources = retrieve(paper_ids, query, top_k)
    context = build_context(sources)
    prompt = templates.format_chat_prompt(context=context, history=history, question=query)
    answer = llm_service.generate(prompt)
    return answer, sources


def generate_summary(paper_id: str, summary_type: str, top_k: int) -> tuple[str, list[SourceChunk]]:
    """
    Summaries retrieve broadly from a single paper (using the summary_type as
    the retrieval query itself, since e.g. "methodology" is a good semantic
    query for methodology-relevant chunks).
    """
    query_hint = summary_type.replace("_", " ")
    sources = retrieve([paper_id], query_hint, top_k)
    context = build_context(sources)
    prompt = templates.format_summary_prompt(summary_type, context)
    content = llm_service.generate(prompt)
    return content, sources


def generate_comparison(paper_ids: list[str], aspects: list[str], top_k_per_paper: int) -> tuple[str, list[SourceChunk]]:
    """Retrieve relevant chunks from EACH paper separately, then compare."""
    all_sources: list[SourceChunk] = []
    query = " ".join(aspects)
    for pid in paper_ids:
        all_sources.extend(retrieve([pid], query, top_k_per_paper))

    context = build_context(all_sources)
    prompt = templates.format_compare_prompt(context, aspects)
    table = llm_service.generate(prompt)
    return table, all_sources
