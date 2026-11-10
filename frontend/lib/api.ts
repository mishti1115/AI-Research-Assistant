import type { ChatResponse, Paper } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* response wasn't JSON — fall back to statusText */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async listPapers(): Promise<Paper[]> {
    const res = await fetch(`${BASE_URL}/api/papers`, { cache: "no-store" });
    return handle<Paper[]>(res);
  },

  async uploadPaper(file: File): Promise<{ paper_id: string; filename: string; status: string }> {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/api/papers/upload`, { method: "POST", body: form });
    return handle(res);
  },

  async deletePaper(paperId: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/api/papers/${paperId}`, { method: "DELETE" });
    await handle(res);
  },

  async agentChat(query: string, paperIds: string[], conversationId?: string): Promise<ChatResponse> {
    const res = await fetch(`${BASE_URL}/api/chat/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, paper_ids: paperIds, conversation_id: conversationId }),
    });
    return handle<ChatResponse>(res);
  },

  async summarize(paperId: string, summaryType: string): Promise<{ content: string; sources: ChatResponse["sources"] }> {
    const res = await fetch(`${BASE_URL}/api/summary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paper_id: paperId, summary_type: summaryType }),
    });
    return handle(res);
  },

  async compare(paperIds: string[], aspects: string[]): Promise<{ table_markdown: string; sources: ChatResponse["sources"] }> {
    const res = await fetch(`${BASE_URL}/api/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paper_ids: paperIds, aspects }),
    });
    return handle(res);
  },

  async citation(paperId: string, style: string): Promise<{ citation: string }> {
    const res = await fetch(`${BASE_URL}/api/citation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paper_id: paperId, style }),
    });
    return handle(res);
  },
};
