"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { SourceChunk } from "@/lib/types";

/**
 * Renders retrieved chunks as small library-index-tab style entries —
 * the page number is the whole point, so it's foregrounded like a real
 * book's tabbed bookmark rather than buried in a footnote.
 */
export default function SourceList({ sources }: { sources: SourceChunk[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (sources.length === 0) return null;

  return (
    <div className="mt-3">
      <p className="text-xs uppercase tracking-wide opacity-50 mb-2">
        Sourced from {sources.length} passage{sources.length > 1 ? "s" : ""}
      </p>
      <div className="space-y-1.5">
        {sources.map((s) => {
          const isOpen = expanded === s.chunk_id;
          return (
            <div key={s.chunk_id} className="index-tab">
              <button
                onClick={() => setExpanded(isOpen ? null : s.chunk_id)}
                className="w-full flex items-center justify-between text-left py-1 group"
              >
                <span className="text-xs font-mono opacity-70 group-hover:opacity-100">
                  {s.paper_title || s.paper_id} · p.{s.page_number}
                </span>
                {isOpen ? (
                  <ChevronUp className="w-3.5 h-3.5 opacity-50" />
                ) : (
                  <ChevronDown className="w-3.5 h-3.5 opacity-50" />
                )}
              </button>
              {isOpen && (
                <p className="text-xs opacity-70 leading-relaxed pb-2 pr-2">{s.text}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
