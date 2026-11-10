"""
Gemini embedding generation and FAISS vector store management.
"""

from __future__ import annotations

import os
import shutil
import math
import time

from google import genai
from google.genai import types

from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.chunker import Chunk

logger = get_logger(__name__)
settings = get_settings()

_embeddings = None


class GeminiEmbeddings(Embeddings):

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing.")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-embedding-001"

    def _embed(self, text: str, task_type: str) -> list[float]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=768,
            ),
        )

        values = response.embeddings[0].values
        norm = math.sqrt(sum(value * value for value in values))

        if norm == 0:
            return values

        return [value / norm for value in values]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        results = []
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = self.client.models.embed_content(
                model=self.model,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768,
                ),
            )

            for embedding in response.embeddings:
                values = embedding.values
                norm = math.sqrt(sum(v * v for v in values))

                if norm == 0:
                    results.append(values)
                else:
                    results.append([v / norm for v in values])

            if i + batch_size < len(texts):
                time.sleep(8)

        return results

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text, "RETRIEVAL_QUERY")


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        logger.info("Initializing Gemini Embeddings")
        _embeddings = GeminiEmbeddings()

    return _embeddings


def _index_path(paper_id: str) -> str:
    return os.path.join(settings.VECTOR_STORE_DIR, paper_id)


def build_index(paper_id: str, chunks: list[Chunk]) -> None:
    if not chunks:
        raise ValueError("Cannot build an index with zero chunks.")

    docs = [
        Document(
            page_content=c.text,
            metadata={**c.metadata, "chunk_id": c.chunk_id},
        )
        for c in chunks
    ]

    logger.info("Embedding %d chunks for paper %s", len(docs), paper_id)

    store = FAISS.from_documents(docs, get_embeddings())

    path = _index_path(paper_id)
    os.makedirs(path, exist_ok=True)

    store.save_local(path)

    logger.info("Saved FAISS index for paper %s at %s", paper_id, path)


def load_index(paper_id: str) -> FAISS | None:
    path = _index_path(paper_id)

    if not os.path.isdir(path):
        return None

    return FAISS.load_local(
        path,
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


def delete_index(paper_id: str) -> None:
    path = _index_path(paper_id)

    if os.path.isdir(path):
        shutil.rmtree(path)
        logger.info("Deleted FAISS index for paper %s", paper_id)


def similarity_search(
    paper_ids: list[str],
    query: str,
    top_k: int,
) -> list[tuple[Document, float]]:

    results: list[tuple[Document, float]] = []

    for paper_id in paper_ids:
        store = load_index(paper_id)

        if store is None:
            logger.warning(
                "No index found for paper_id=%s, skipping",
                paper_id,
            )
            continue

        hits = store.similarity_search_with_score(query, k=top_k)

        for doc, distance in hits:
            similarity = 1.0 / (1.0 + distance)
            results.append((doc, similarity))

    results.sort(key=lambda pair: pair[1], reverse=True)

    return results[:top_k]