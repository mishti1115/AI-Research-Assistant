# AI Research Paper Assistant — Frontend

Next.js 14 (App Router) + TypeScript + Tailwind dashboard for the backend API.

## Design language: "The Reading Room"

A quiet academic library at night — deep forest ink background, brass accent
(library lamps, book bindings), serif display type for headings, sans body
text. The signature element is the **index tab**: every AI answer's sources
are shown as small tabbed citations with page numbers, echoing a book's
bookmark tabs, so "where did this come from" is always one click away.

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local     # point NEXT_PUBLIC_API_BASE_URL at your backend
npm run dev
```

Visit `http://localhost:3000`. Make sure the backend is running at the URL in `.env.local`.

## Structure

```
frontend/
├── app/
│   ├── layout.tsx        # Fonts, root HTML shell
│   ├── page.tsx           # Dashboard: sidebar + view switcher
│   └── globals.css        # Design tokens, "reading room" theme
├── components/
│   ├── Sidebar.tsx         # Nav + dark/light toggle
│   ├── UploadPanel.tsx     # Drag-and-drop PDF upload
│   ├── PaperLibrary.tsx    # Paper list, status, expandable detail
│   ├── SummaryPanel.tsx    # 12 prompt-engineered summary types + citations
│   ├── ChatInterface.tsx   # Agent-routed chat with paper scoping
│   ├── ComparisonScreen.tsx# Multi-paper comparison table
│   └── SourceList.tsx      # The "index tab" citation component
└── lib/
    ├── api.ts              # Typed fetch wrapper around the backend
    └── types.ts            # Shared TS types mirroring backend Pydantic models
```

## Views

- **Paper Library** — upload PDFs, watch ingestion status, expand a ready
  paper to generate any of the 12 summary types or a citation (APA/IEEE/MLA/BibTeX).
- **Chat** — natural-language Q&A routed through the backend's research agent;
  scope to specific papers or leave unscoped to search the whole library.
  Answers link back to source page numbers.
- **Compare** — pick 2+ papers, get a grounded markdown comparison table
  (dataset, architecture, accuracy, novelty, limitations, future work).

## Notes / what's deferred

This is Phase 2 of the project (backend was Phase 1). Not yet built:
knowledge graph view, flashcards, timeline view, persisted conversation
history across sessions (currently in-memory per browser session), and
highlighting the exact retrieved paragraph inline over a PDF preview
(currently shown as an expandable text excerpt instead).
