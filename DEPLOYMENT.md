# Deployment Guide

Two supported paths: **quick local/self-hosted** (Docker Compose) and
**cloud** (Vercel + Render/AWS, matching the project brief's tech stack).

## Option A — Docker Compose (local or any VM) — free, no API key

```bash
docker compose up --build
# one-time: pull the model into the Ollama container
docker exec -it $(docker ps -qf "ancestor=ollama/ollama") ollama pull llama3.2
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

This is the fastest way to demo the whole project end-to-end, entirely free.
First upload after starting will be slower while the embedding model
downloads and caches (~90MB, one-time).

## Option B — Cloud (Vercel + Render)

⚠️ **Note on Ollama in the cloud:** Ollama needs a real machine with enough
RAM (4GB+ free for a small model like `llama3.2`), which most free-tier cloud
plans don't offer. For a cloud demo, either (a) run Ollama on a paid VM with
enough RAM, or (b) switch `LLM_PROVIDER` to `openai` or `gemini` in the
backend's environment variables for the cloud deployment only, while still
using free local embeddings either way (sentence-transformers has no such
requirement and runs fine on Render's free tier).

### Backend → Render

1. Push this repo to GitHub.
2. On Render: **New → Web Service**, connect the repo, set root directory to `backend`.
3. Render auto-detects the `Dockerfile`, or set manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `backend/.env.example`. For a free cloud
   demo, set `LLM_PROVIDER=gemini` (Gemini has a free API tier) and add
   `GEMINI_API_KEY` — Ollama isn't practical on Render's free plan.
5. Note the deployed URL, e.g. `https://your-app.onrender.com`.

**AWS alternative:** build the backend image (`docker build -t rpa-backend ./backend`),
push to ECR, and run on ECS Fargate or App Runner with the same env vars.
Attach an EFS volume (or swap `paper_registry.py`/`vector_store.py` for S3 +
a managed vector DB) if you need indexes to survive container restarts. If
you want Ollama in the cloud, run it as a second container/task with at
least 4GB RAM and point `OLLAMA_BASE_URL` at it.

### Frontend → Vercel

1. On Vercel: **New Project**, import the repo, set root directory to `frontend`.
2. Framework preset: Next.js (auto-detected).
3. Add environment variable: `NEXT_PUBLIC_API_BASE_URL` = your Render backend URL.
4. Deploy. Vercel handles build/CDN/HTTPS automatically.

### Post-deploy checklist

- [ ] Backend `CORS_ORIGINS` in `.env` includes your Vercel frontend URL
- [ ] `/health` on the backend returns `{"status": "ok"}`
- [ ] Upload a test PDF end-to-end through the deployed frontend
- [ ] Vector store volume is persistent (or accept in-memory/ephemeral for a demo deploy)

## Environment variables reference

| Variable | Where | Purpose |
|---|---|---|
| `LLM_PROVIDER` | backend | `ollama` (free/local, default), `openai`, or `gemini` |
| `OLLAMA_BASE_URL` / `OLLAMA_CHAT_MODEL` | backend | Only used when `LLM_PROVIDER=ollama` |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | backend | Only needed if you switch to a paid provider |
| `EMBEDDING_MODEL` | backend | Free local sentence-transformers model, no key needed |
| `CORS_ORIGINS` | backend | Must include your deployed frontend origin |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | Points the UI at your backend |

## Known limitation for cloud deploys

`paper_registry.py` and the FAISS indexes in `vector_store.py` are currently
local-disk/in-memory (see backend README's "what's next"). On ephemeral
platforms (e.g. Render's default disk, most serverless runtimes) this means
uploaded papers won't survive a redeploy or restart. Fine for a demo; for a
persistent production deployment, swap in Postgres for paper metadata and
S3 + a managed vector store (Pinecone/pgvector) before going live.
