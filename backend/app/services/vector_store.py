"""
Embedding generation and FAISS vector store management.

Each paper gets its own FAISS index on disk (app/data/vector_store/<paper_id>/)
so papers can be added/removed independently. A lightweight in-memory registry
tracks which paper_ids exist so multi-paper queries know what to load.
"""
from __future__ import annotations

import os
import shutil

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.chunker import Chunk

logger = get_logger(__name__)
settings = get_settings()

_embeddings = None


def get_embeddings():
    """
    Lazily construct the embeddings model. Runs fully locally on CPU via
    sentence-transformers — no API key, no per-call cost. The model weights
    (~90MB for all-MiniLM-L6-v2) download once from HuggingFace Hub and are
    cached under ~/.cache/huggingface on first use.
    """
    global _embeddings
    if _embeddings is None:
        logger.info("Loading local embedding model: %s (first run downloads weights)",
                    settings.EMBEDDING_MODEL)
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def _index_path(paper_id: str) -> str:
    return os.path.join(settings.VECTOR_STORE_DIR, paper_id)


def build_index(paper_id: str, chunks: list[Chunk]) -> None:
    """Embed all chunks for a paper and persist a FAISS index to disk."""
    if not chunks:
        raise ValueError("Cannot build an index with zero chunks.")

    docs = [
        Document(page_content=c.text, metadata={**c.metadata, "chunk_id": c.chunk_id})
        for c in chunks
    ]
    logger.info("Embedding %d chunks for paper %s", len(docs), paper_id)
    store = FAISS.from_documents(docs, get_embeddings())

    path = _index_path(paper_id)
    os.makedirs(path, exist_ok=True)
    store.save_local(path)
    logger.info("Saved FAISS index for paper %s at %s", paper_id, path)


def load_index(paper_id: str) -> FAISS | None:
    """Load a single paper's FAISS index from disk, or None if it doesn't exist."""
    path = _index_path(paper_id)
    if not os.path.isdir(path):
        return None
    return FAISS.load_local(path, get_embeddings(), allow_dangerous_deserialization=True)


def delete_index(paper_id: str) -> None:
    path = _index_path(paper_id)
    if os.path.isdir(path):
        shutil.rmtree(path)
        logger.info("Deleted FAISS index for paper %s", paper_id)


def similarity_search(
    paper_ids: list[str], query: str, top_k: int
) -> list[tuple[Document, float]]:
    """
    Search across one or more papers' indexes and return the globally
    top-k (document, score) pairs, sorted by relevance (lower distance = better,
    normalized to similarity here so higher = better for the caller).
    """
    results: list[tuple[Document, float]] = []
    for paper_id in paper_ids:
        store = load_index(paper_id)
        if store is None:
            logger.warning("No index found for paper_id=%s, skipping", paper_id)
            continue
        # similarity_search_with_score returns (doc, L2 distance); lower is better
        hits = store.similarity_search_with_score(query, k=top_k)
        for doc, distance in hits:
            similarity = 1.0 / (1.0 + distance)  # convert distance -> a 0-1-ish similarity
            results.append((doc, similarity))

    results.sort(key=lambda pair: pair[1], reverse=True)
    return results[:top_k]
