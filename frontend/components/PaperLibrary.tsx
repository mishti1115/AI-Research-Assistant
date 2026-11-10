"use client";

import { useEffect, useState } from "react";
import { FileText, Trash2, Loader2, AlertCircle, CheckCircle2, Quote } from "lucide-react";
import { api } from "@/lib/api";
import type { Paper } from "@/lib/types";
import { SUMMARY_TYPES } from "@/lib/types";
import UploadPanel from "./UploadPanel";
import SummaryPanel from "./SummaryPanel";

const STATUS_META: Record<Paper["status"], { label: string; icon: React.ElementType; className: string }> = {
  ready: { label: "Ready", icon: CheckCircle2, className: "text-moss-400" },
  processing: { label: "Processing…", icon: Loader2, className: "text-brass-400 animate-spin" },
  uploaded: { label: "Queued", icon: Loader2, className: "text-brass-400" },
  failed: { label: "Failed", icon: AlertCircle, className: "text-red-400" },
};

export default function PaperLibrary() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Paper | null>(null);

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await api.listPapers();
      setPapers(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleDelete = async (paperId: string) => {
    await api.deletePaper(paperId);
    if (selected?.paper_id === paperId) setSelected(null);
    refresh();
  };

  return (
    <div className="max-w-5xl mx-auto px-8 py-10">
      <h1 className="font-display text-3xl mb-1">Paper Library</h1>
      <p className="opacity-60 mb-8 text-sm">
        Upload research papers to build a searchable, citable knowledge base.
      </p>

      <div className="mb-10">
        <UploadPanel onUploaded={refresh} />
      </div>

      {loading ? (
        <p className="opacity-60 text-sm">Loading papers…</p>
      ) : papers.length === 0 ? (
        <div className="index-tab py-4 opacity-70 text-sm">
          No papers yet. Upload one above to start asking questions.
        </div>
      ) : (
        <div className="space-y-2">
          {papers.map((p) => {
            const meta = STATUS_META[p.status];
            const StatusIcon = meta.icon;
            return (
              <div key={p.paper_id}>
                <div
                  onClick={() => p.status === "ready" && setSelected(selected?.paper_id === p.paper_id ? null : p)}
                  className={`flex items-center gap-4 px-4 py-3 rounded-md border hairline transition-colors ${
                    p.status === "ready" ? "cursor-pointer hover:bg-ink-800/40" : ""
                  } ${selected?.paper_id === p.paper_id ? "bg-ink-800/50" : ""}`}
                >
                  <FileText className="w-5 h-5 text-brass-500 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{p.title || p.filename}</p>
                    <p className="text-xs opacity-50 font-mono">
                      {p.num_pages ? `${p.num_pages} pages · ${p.num_chunks} chunks` : p.filename}
                    </p>
                    {p.error && <p className="text-xs text-red-400 mt-1">{p.error}</p>}
                  </div>
                  <div className={`flex items-center gap-1.5 text-xs shrink-0 ${meta.className}`}>
                    <StatusIcon className="w-3.5 h-3.5" />
                    {meta.label}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(p.paper_id);
                    }}
                    className="opacity-40 hover:opacity-100 hover:text-red-400 transition-opacity shrink-0"
                    aria-label={`Delete ${p.filename}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {selected?.paper_id === p.paper_id && (
                  <div className="mt-2 mb-4 index-tab">
                    <SummaryPanel paperId={p.paper_id} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
