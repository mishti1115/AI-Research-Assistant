"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export default function UploadPanel({ onUploaded }: { onUploaded: () => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;
      setError(null);
      setIsUploading(true);
      try {
        for (const file of Array.from(files)) {
          if (!file.name.toLowerCase().endsWith(".pdf")) {
            throw new Error(`${file.name} isn't a PDF — only PDF files are supported.`);
          }
          await api.uploadPaper(file);
        }
        onUploaded();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed.");
      } finally {
        setIsUploading(false);
      }
    },
    [onUploaded]
  );

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer border-2 border-dashed rounded-lg px-6 py-10 text-center transition-colors ${
          isDragging ? "border-brass-500 bg-brass-500/5" : "border-ink-700 hover:border-brass-500/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        {isUploading ? (
          <Loader2 className="w-8 h-8 mx-auto mb-3 text-brass-500 animate-spin" />
        ) : (
          <UploadCloud className="w-8 h-8 mx-auto mb-3 text-brass-500" />
        )}
        <p className="font-display text-base">
          {isUploading ? "Reading your paper…" : "Drop a research paper here"}
        </p>
        <p className="text-xs opacity-60 mt-1">PDF only, up to 50MB · or click to browse</p>
      </div>
      {error && (
        <p className="text-sm text-red-400 mt-3 index-tab border-red-500/60">{error}</p>
      )}
    </div>
  );
}
