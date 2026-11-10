"use client";

import { useState } from "react";
import { Loader2, Quote } from "lucide-react";
import { api } from "@/lib/api";
import { SUMMARY_TYPES } from "@/lib/types";
import SourceList from "./SourceList";
import type { SourceChunk } from "@/lib/types";

const CITATION_STYLES = ["apa", "ieee", "mla", "bibtex"];

export default function SummaryPanel({ paperId }: { paperId: string }) {
  const [summaryType, setSummaryType] = useState("executive");
  const [content, setContent] = useState<string | null>(null);
  const [sources, setSources] = useState<SourceChunk[]>([]);
  const [loading, setLoading] = useState(false);
  const [citation, setCitation] = useState<string | null>(null);
  const [citationStyle, setCitationStyle] = useState("apa");

  const generate = async (type: string) => {
    setSummaryType(type);
    setLoading(true);
    setContent(null);
    try {
      const res = await api.summarize(paperId, type);
      setContent(res.content);
      setSources(res.sources);
    } finally {
      setLoading(false);
    }
  };

  const getCitation = async (style: string) => {
    setCitationStyle(style);
    const res = await api.citation(paperId, style);
    setCitation(res.citation);
  };

  return (
    <div className="py-4 space-y-4">
      <div className="flex flex-wrap gap-1.5">
        {SUMMARY_TYPES.map((t) => (
          <button
            key={t.value}
            onClick={() => generate(t.value)}
            className={`text-xs px-2.5 py-1.5 rounded-full border hairline transition-colors ${
              summaryType === t.value && content
                ? "bg-brass-500/20 border-brass-500/60 text-brass-300"
                : "opacity-70 hover:opacity-100 hover:border-brass-500/40"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm opacity-60 py-4">
          <Loader2 className="w-4 h-4 animate-spin" /> Generating {summaryType.replace("_", " ")}…
        </div>
      )}

      {content && !loading && (
        <div className="prose prose-invert prose-sm max-w-none font-body whitespace-pre-wrap leading-relaxed">
          {content}
        </div>
      )}

      {sources.length > 0 && !loading && <SourceList sources={sources} />}

      <div className="pt-3 border-t hairline">
        <div className="flex items-center gap-2 mb-2">
          <Quote className="w-3.5 h-3.5 text-brass-500" />
          <span className="text-xs uppercase tracking-wide opacity-60">Cite this paper</span>
        </div>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {CITATION_STYLES.map((s) => (
            <button
              key={s}
              onClick={() => getCitation(s)}
              className={`text-xs px-2 py-1 rounded border hairline uppercase ${
                citationStyle === s && citation ? "bg-brass-500/20 border-brass-500/60" : "opacity-60 hover:opacity-100"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        {citation && (
          <pre className="text-xs font-mono bg-ink-800/50 rounded p-3 whitespace-pre-wrap">{citation}</pre>
        )}
      </div>
    </div>
  );
}
