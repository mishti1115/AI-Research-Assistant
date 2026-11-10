# AI Research Paper Assistant — Backend (Phase 1)

A RAG-powered API for uploading research papers and chatting with, summarizing,
and comparing them — with citations back to the exact page a claim came from.

This is **Phase 1** of the full project spec: a complete, working backend core.
See **"What's built vs. what's next"** below for the honest scope breakdown.

## Architecture

```
User
  │
  ▼
FastAPI Backend  ──────────────────────────────────────────┐
  │                                                          │
  ├─ /api/papers/upload  → PDF Parser (PyMuPDF)              │
  │                           │                               │
  │                           ▼                               │
  │                        Chunker (RecursiveCharacterSplitter)│
  │                           │                               │
  │                           ▼                               │
  │                        Embeddings (OpenAI text-embedding-3-large)
  │                           │                               │
  │                           ▼                               │
  │                        FAISS Vector Store (per-paper index)
  │                                                          │
  ├─ /api/chat            → Research Agent (intent routing)   │
  ├─ /api/chat/agent         │                                │
  ├─ /api/summary            ▼                                │
  ├─ /api/compare         Retriever → Prompt Templates → LLM  │
  └─ /api/citation           (grounded, anti-hallucination)   │
                                                          ────┘
```

## Folder structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, routers, error handling
│   ├── core/
│   │   ├── config.py             # Settings (env-driven)
│   │   └── logging_config.py
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── services/
│   │   ├── pdf_parser.py         # PyMuPDF text extraction, per-page
│   │   ├── chunker.py            # Page-aware recursive chunking
│   │   ├── vector_store.py       # FAISS index build/load/search
│   │   ├── llm_service.py        # OpenAI/Gemini generation wrapper
│   │   ├── rag_service.py        # Orchestrates ingest + retrieve + generate
│   │   └── paper_registry.py     # In-memory paper metadata store
│   ├── prompts/
│   │   └── templates.py          # All grounded prompt templates
│   ├── agents/
│   │   └── research_agent.py     # Intent → workflow routing
│   ├── routers/
│   │   ├── papers.py             # Upload / list / delete
│   │   ├── chat.py               # /chat and /chat/agent
│   │   ├── summary.py            # /summary and /compare
│   │   └── citation.py           # /citation
│   └── data/
│       ├── uploads/              # Saved PDFs
│       └── vector_store/         # Per-paper FAISS indexes
├── requirements.txt
├── Dockerfile
├── .env.example
└── .gitignore
```

## Setup (100% free — no API key needed)

This runs entirely on your machine: **Ollama** for the LLM, a local
**sentence-transformers** model for embeddings. Nothing costs money and
nothing leaves your machine.

```bash
# 1. Install Ollama: https://ollama.com (one-time)
ollama pull llama3.2        # ~2GB download, one-time
ollama serve                 # usually starts automatically after install

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # defaults already point at Ollama, no editing needed
uvicorn app.main:app --reload
```

First upload will take a little longer than usual — it downloads the
~90MB embedding model from HuggingFace Hub once, then caches it locally.

API docs: `http://localhost:8000/docs`

**Want a hosted model instead?** Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=gemini`
in `.env` and add the matching API key — the code supports both, this is just
the free default.

### Docker

The root-level `docker-compose.yml` (one level up) runs Ollama + backend +
frontend together — see the main [README](../README.md). To run just this
service standalone against an Ollama already running on your host:

```bash
docker build -t research-assistant-backend .
docker run -p 8000:8000 --env-file .env \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  research-assistant-backend
```

## Key endpoints

| Method | Path                  | Purpose                                             |
|--------|------------------------|------------------------------------------------------|
| POST   | `/api/papers/upload`  | Upload a PDF, run full ingestion pipeline           |
| GET    | `/api/papers`         | List all papers + status                            |
| DELETE | `/api/papers/{id}`    | Remove a paper and its index                         |
| POST   | `/api/chat`           | Direct grounded Q&A over selected paper(s)          |
| POST   | `/api/chat/agent`     | Natural-language entry point; agent routes workflow |
| POST   | `/api/summary`        | Generate one of 12 summary types for a paper        |
| POST   | `/api/compare`        | Compare 2+ papers as a markdown table               |
| POST   | `/api/citation`       | Generate APA/IEEE/MLA/BibTeX citation                |

## How hallucination is reduced

Every prompt in `app/prompts/templates.py` follows the same pattern:
1. The LLM is explicitly told to answer **only** from the retrieved context.
2. It's instructed to say so when context is insufficient, rather than guess.
3. Retrieved chunks carry their page number end-to-end, so every answer can be
   traced back to `SourceChunk.page_number` — this is what powers citations
   and "highlight the source paragraph" in the response payload.

## What's built vs. what's next

**Built (Phase 1 — this delivery):**
- Full RAG pipeline: parse → chunk → embed → FAISS → retrieve → generate
- **Runs entirely free/local by default**: Ollama (LLM) + sentence-transformers
  (embeddings), no API key required. OpenAI/Gemini remain supported as opt-in
  paid alternatives via `LLM_PROVIDER` in `.env`.
- 12 grounded prompt templates (summary variants, ELI10, viva, quiz, etc.)
- Multi-paper support and comparison-table generation
- Rule-based research agent that routes chat vs. summary vs. compare
- Citation generation (APA/IEEE/MLA/BibTeX) — best-effort from extracted title
- Dockerized, logged, typed, PEP8-formatted FastAPI backend

**Deliberately deferred (needs its own dedicated pass):**
- Next.js/React/Tailwind frontend (dashboard, chat UI, comparison screen)
- Swap `research_agent.py`'s rule-based router for a LangGraph `StateGraph`
  with an LLM router node + tool-calling (the interface — `decide()` → 
  `AgentDecision` — is already the extension point for this)
- Persistent database for paper metadata (currently in-memory — resets on
  restart; `paper_registry.py` is written as a swappable interface)
- Knowledge graph, flashcards, timeline-of-research, semantic bookmarks
- OCR fallback for scanned PDFs (currently raises `PDFParsingError`)
- Conversation memory persistence (currently stateless per-request)
- CI/CD, cloud deployment configs (Vercel/Render/AWS), demo script, report

## Testing it manually

```bash
# 1. Upload a paper
curl -F "file=@/path/to/paper.pdf" http://localhost:8000/api/papers/upload

# 2. Ask a question (use the returned paper_id)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What dataset did the authors use?", "paper_ids": ["<paper_id>"]}'

# 3. Get an executive summary
curl -X POST http://localhost:8000/api/summary \
  -H "Content-Type: application/json" \
  -d '{"paper_id": "<paper_id>", "summary_type": "executive"}'
```
