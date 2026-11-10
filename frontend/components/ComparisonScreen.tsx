"use client";

import { useEffect, useState } from "react";
import { Scale, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/api";
import type { Paper, SourceChunk } from "@/lib/types";
import SourceList from "./SourceList";

const DEFAULT_ASPECTS = ["dataset", "architecture", "accuracy", "novelty", "limitations", "future_work"];

export default function ComparisonScreen() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [table, setTable] = useState<string | null>(null);
  const [sources, setSources] = useState<SourceChunk[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listPapers().then((all) => setPapers(all.filter((p) => p.status === "ready")));
  }, []);

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const runComparison = async () => {
    if (selected.size < 2) {
      setError("Select at least 2 papers to compare.");
      return;
    }
    setError(null);
    setLoading(true);
    setTable(null);
    try {
      const res = await api.compare(Array.from(selected), DEFAULT_ASPECTS);
      setTable(res.table_markdown);
      setSources(res.sources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-8 py-10">
      <div className="flex items-center gap-2 mb-1">
        <Scale className="w-5 h-5 text-brass-500" />
        <h1 className="font-display text-3xl">Compare Papers</h1>
      </div>
      <p className="opacity-60 mb-8 text-sm">
        Select two or more papers to generate a side-by-side comparison table, grounded in each paper&apos;s own text.
      </p>

      {papers.length < 2 ? (
        <p className="text-sm opacity-60">You need at least 2 ready papers in your library to compare.</p>
      ) : (
        <>
          <div className="flex flex-wrap gap-1.5 mb-4">
            {papers.map((p) => (
              <button
                key={p.paper_id}
                onClick={() => toggle(p.paper_id)}
                className={`text-xs px-2.5 py-1.5 rounded-full border hairline transition-colors ${
                  selected.has(p.paper_id)
                    ? "bg-brass-500/20 border-brass-500/60 text-brass-300"
                    : "opacity-60 hover:opacity-100"
                }`}
              >
                {p.title || p.filename}
              </button>
            ))}
          </div>

          <button
            onClick={runComparison}
            disabled={loading}
            className="bg-brass-500 hover:bg-brass-400 disabled:opacity-40 text-ink-950 text-sm font-medium px-4 py-2 rounded-md transition-colors"
          >
            {loading ? "Comparing…" : "Generate comparison"}
          </button>

          {error && <p className="text-sm text-red-400 mt-3">{error}</p>}

          {loading && (
            <div className="flex items-center gap-2 text-sm opacity-60 mt-6">
              <Loader2 className="w-4 h-4 animate-spin" /> Reading each paper&apos;s methodology, results, and limitations…
            </div>
          )}

          {table && !loading && (
            <div className="mt-8">
              <div className="prose prose-invert prose-sm max-w-none overflow-x-auto">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{table}</ReactMarkdown>
              </div>
              <SourceList sources={sources} />
            </div>
          )}
        </>
      )}
    </div>
  );
}
