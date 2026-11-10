# AI Research Paper Assistant

An enterprise-grade RAG application for chatting with, summarizing, and
comparing research papers — every answer grounded in and traceable back to
the source PDF's page number.

```
                User
                  │
                  ▼
          React / Next.js Frontend  (Tailwind, TypeScript)
                  │  REST (JSON)
                  ▼
            FastAPI Backend
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
PDF Processing          AI Research Agent
(PyMuPDF)               (intent → workflow routing)
      │                       │
      ▼                       ▼
Text Chunking            Prompt Templates
(page-aware,             (12 grounded, anti-
recursive splitter)       hallucination templates)
      │                       │
      ▼                       ▼
Embedding Model  ──────▶ FAISS Vector Database ◀──────  Retriever (top-k)
(sentence-transformers,        │
 local, free)                  ▼
                          Ollama (llama3.2, local)
                          — or OpenAI / Gemini if configured
                                │
                                ▼
                      Response + Page-Level Citations
```

## What this is

| Layer | Tech | Status |
|---|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind | ✅ Built |
| Backend API | FastAPI, Python | ✅ Built |
| RAG pipeline | PyMuPDF → LangChain splitter → FAISS | ✅ Built |
| Embeddings | sentence-transformers (local, free, CPU) | ✅ Built — default |
| LLM | Ollama / llama3.2 (local, free) — OpenAI/Gemini optional | ✅ Built — free by default |
| Agent | Rule-based intent router | ✅ Built (LangGraph upgrade path documented) |
| Deployment | Docker Compose (incl. Ollama), Vercel + Render/AWS guide | ✅ Built |
| Database | In-memory registry | ⚠️ Swappable stub — see "Roadmap" |
| Advanced features (knowledge graph, flashcards, OCR, etc.) | — | 🔜 Not built |

## Quick start (100% free — no API key needed)

Runs entirely on your machine: Ollama serves the LLM, a local
sentence-transformers model handles embeddings. Nothing costs money.

```bash
git clone <this-repo>
cd ai-research-assistant

# One-time: install Ollama (https://ollama.com) and pull a model
ollama pull llama3.2

# Backend
cd backend
cp .env.example .env        # defaults already point at Ollama — no editing needed
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload &

# Frontend (new terminal)
cd ../frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. Full API docs at `http://localhost:8000/docs`.

Or, one command with Docker (spins up Ollama + backend + frontend together):

```bash
docker compose up --build
# then, one-time, pull the model into the Ollama container:
docker exec -it $(docker ps -qf "ancestor=ollama/ollama") ollama pull llama3.2
```

**Prefer a hosted model?** Set `LLM_PROVIDER=openai` or `gemini` in
`backend/.env` and add the matching API key — both remain fully supported,
Ollama is just the free default.

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for cloud deployment (Vercel + Render/AWS).

## Project structure

```
ai-research-assistant/
├── backend/           # FastAPI + RAG pipeline — see backend/README.md
├── frontend/          # Next.js dashboard — see frontend/README.md
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md          # you are here
```

## Core features

- **Upload & ingest** PDFs → text extraction → chunking → embeddings → FAISS index
- **Grounded chat** — every answer is generated only from retrieved context; the
  model is instructed to say "not covered" rather than guess
- **12 prompt-engineered summary modes**: executive/detailed summary, contributions,
  methodology, dataset, results, limitations, future work, novelty, practical
  applications, ELI10, viva prep, interview questions, quiz
- **Multi-paper comparison** — generates a markdown table across papers on
  dataset / architecture / accuracy / novelty / limitations / future work
- **Page-level citations** — every retrieved chunk carries its source page number,
  shown in the UI as an "index tab" so any claim can be traced back to the PDF
- **Citation generator** — APA / IEEE / MLA / BibTeX
- **AI research agent** — routes a natural-language query to the right workflow
  (chat vs. summary vs. comparison) without the user picking manually

## Prompt engineering approach

All prompts (`backend/app/prompts/templates.py`) share one grounding rule:
answer only from the provided context, and explicitly say when the context is
insufficient. This is the main lever this system uses to reduce hallucination,
combined with returning the exact source passages alongside every answer so a
user can verify a claim in one click.

## Roadmap / honest scope notes

This was built in two phases and is a strong reference implementation, not a
finished enterprise product. What's genuinely deferred, in priority order:

1. **Persistent storage** — swap the in-memory `paper_registry.py` for Postgres,
   and FAISS-on-disk for a managed vector DB (Pinecone/pgvector) if you need
   uploads to survive redeploys.
2. **LangGraph agent** — `research_agent.py`'s `decide()` function is a clean
   rule-based router today; it's built as the exact seam to swap in a LangGraph
   `StateGraph` with an LLM router node and tool-calling.
3. **OCR fallback** for scanned PDFs (currently raises a clear error instead).
4. **Advanced features** not yet built: knowledge graph, flashcards, timeline
   of research, semantic bookmarks, conversation memory persisted across
   sessions, inline PDF viewer with highlighted source paragraphs.
5. **Testing, CI/CD, demo video script, and formal project report** — none of
   these exist yet; happy to generate any of them next.

## License

MIT — see individual `backend/` and `frontend/` folders; add a `LICENSE` file
before publishing if you need one committed to the repo.
