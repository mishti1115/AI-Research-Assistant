"""
Upload endpoints: accept PDF(s), run ingestion, expose paper library.
"""
from __future__ import annotations

import os
import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.schemas import Paper, PaperStatus, UploadResponse
from app.services import paper_registry, rag_service, vector_store

router = APIRouter(prefix="/api/papers", tags=["papers"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("/upload", response_model=UploadResponse)
async def upload_paper(file: UploadFile = File(...)):
    """
    Accept a PDF upload, save it to disk, and kick off ingestion synchronously.
    (Synchronous for simplicity/determinism in this reference implementation;
    swap to BackgroundTasks + a status-polling endpoint for large files.)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    size_limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    with open(dest_path, "wb") as out:
        total = 0
        while chunk := await file.read(1024 * 1024):
            total += len(chunk)
            if total > size_limit:
                out.close()
                os.remove(dest_path)
                raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_MB}MB limit.")
            out.write(chunk)

    logger.info("Saved upload %s -> %s", file.filename, dest_path)
    paper = rag_service.ingest_paper(dest_path, file.filename)

    if paper.status == PaperStatus.FAILED:
        raise HTTPException(status_code=422, detail=paper.error or "Ingestion failed.")

    return UploadResponse(paper_id=paper.paper_id, filename=paper.filename, status=paper.status)


@router.get("", response_model=list[Paper])
async def list_papers():
    """Return the paper library (all uploaded papers and their status)."""
    return paper_registry.list_all()


@router.get("/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    paper = paper_registry.get(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    paper = paper_registry.get(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    vector_store.delete_index(paper_id)
    paper_registry.delete(paper_id)
    return {"status": "deleted", "paper_id": paper_id}
