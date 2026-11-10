"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Loader2, BookOpen } from "lucide-react";
import { api } from "@/lib/api";
import type { Message, Paper } from "@/lib/types";
import SourceList from "./SourceList";

export default function ChatInterface() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPapers, setSelectedPapers] = useState<Set<string>>(new Set());
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.listPapers().then((all) => setPapers(all.filter((p) => p.status === "ready")));
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const togglePaper = (id: string) => {
    setSelectedPapers((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const send = async () => {
    const query = input.trim();
    if (!query || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: query }]);
    setLoading(true);
    try {
      const res = await api.agentChat(query, Array.from(selectedPapers), conversationId);
      setConversationId(res.conversation_id);
      setMessages((m) => [...m, { role: "assistant", content: res.answer, sources: res.sources }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Something went wrong: ${err instanceof Error ? err.message : "unknown error"}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      {/* Paper scope selector */}
      <div className="px-8 pt-8 pb-4 border-b hairline">
        <h1 className="font-display text-2xl mb-3">Chat with your papers</h1>
        {papers.length === 0 ? (
          <p className="text-sm opacity-60">No papers ready yet — upload one from the Library tab first.</p>
        ) : (
          <div className="flex flex-wrap gap-1.5">
            {papers.map((p) => (
              <button
                key={p.paper_id}
                onClick={() => togglePaper(p.paper_id)}
                className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-full border hairline transition-colors ${
                  selectedPapers.has(p.paper_id)
                    ? "bg-brass-500/20 border-brass-500/60 text-brass-300"
                    : "opacity-60 hover:opacity-100"
                }`}
              >
                <BookOpen className="w-3 h-3" />
                {p.title || p.filename}
              </button>
            ))}
          </div>
        )}
        <p className="text-xs opacity-40 mt-2">
          {selectedPapers.size === 0 ? "Searching across all papers" : `Scoped to ${selectedPapers.size} selected`}
        </p>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="opacity-50 text-sm py-10 text-center">
            Ask about methodology, results, limitations — or say &quot;compare X and Y&quot; to get a table.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "flex justify-end" : ""}>
            <div className={m.role === "user" ? "max-w-lg bg-brass-500/15 rounded-lg px-4 py-2.5 text-sm" : "max-w-2xl"}>
              {m.role === "assistant" ? (
                <>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap font-body">{m.content}</p>
                  {m.sources && m.sources.length > 0 && <SourceList sources={m.sources} />}
                </>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-sm opacity-50">
            <Loader2 className="w-4 h-4 animate-spin" /> Reading the relevant pages…
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-8 py-5 border-t hairline">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Ask a question about your papers…"
            rows={1}
            className="flex-1 resize-none bg-ink-800/50 rounded-md px-4 py-3 text-sm outline-none border hairline focus:border-brass-500/60"
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="shrink-0 bg-brass-500 hover:bg-brass-400 disabled:opacity-30 disabled:hover:bg-brass-500 text-ink-950 rounded-md p-3 transition-colors"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
