"""
Paper registry.

A simple in-memory store for paper metadata, keyed by paper_id. This is
intentionally swappable: in production replace this with a real database
(e.g. Postgres via SQLAlchemy) behind the same get/set/list/delete interface.
"""
from __future__ import annotations

import threading

from app.models.schemas import Paper

_lock = threading.Lock()
_papers: dict[str, Paper] = {}


def save(paper: Paper) -> None:
    with _lock:
        _papers[paper.paper_id] = paper


def get(paper_id: str) -> Paper | None:
    return _papers.get(paper_id)


def list_all() -> list[Paper]:
    return list(_papers.values())


def delete(paper_id: str) -> None:
    with _lock:
        _papers.pop(paper_id, None)


def all_ready_ids() -> list[str]:
    return [p.paper_id for p in _papers.values() if p.status == "ready"]
